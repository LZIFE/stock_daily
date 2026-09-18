"""构建离线快照 —— 全市场 4898 只跑一遍，运行时只查表。

为什么必须有这一层：核心分的分位、`pct_vol`、`pct_turn`、`amt_pctl`
全是**横截面量**，单只股票单独算没有意义。所以：

    构建期（本脚本，约 1–2 分钟）      →  运行时（API，毫秒级）
    全市场算一遍 + 排好序 + 算坏率表   →  按代码查表，不重算

用法:
    python -m app.build_snapshot                 # 用缓存最后一天
    python -m app.build_snapshot --asof 2026-07-31
    python -m app.build_snapshot --workers 8
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from . import badrate, book_rules, config, scoring, xsec
from .paths import CACHE_DIR, POOL_JSON, SNAPSHOT_DIR

def scan_universe():
    return sorted(p.stem for p in CACHE_DIR.glob("*.json") if not p.name.startswith("_"))


def load_names():
    """代码→名称。_candidate_pool.json 实测覆盖 4898/4898 = 100%。"""
    try:
        return {x["code"]: x.get("name", "") for x in json.load(open(POOL_JSON, encoding="utf-8"))
                if x.get("code")}
    except Exception:
        return {}


def _worker(job):
    """子进程 worker。

    macOS 默认 spawn，**不会**继承父进程的全局变量 —— 所以 asof 必须显式传参。
    """
    code, asof = job
    fp = CACHE_DIR / f"{code}.json"
    try:
        d = json.load(open(fp))
    except Exception:
        return code, None, "parse_error"
    if not isinstance(d, dict):
        return code, None, "malformed"
    k, fin = d.get("k") or [], d.get("fin") or []
    if len(k) < scoring.MIN_KLINE or not fin:
        return code, None, "short_history"
    rec = scoring.build_intermediate(code, k, fin, asof)
    if rec is None:
        return code, None, "no_asof_or_window"
    return code, rec, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    t0 = time.time()
    codes = scan_universe()
    if not codes:
        print(f"❌ 缓存目录为空或不存在: {CACHE_DIR}")
        return 2

    if args.asof:
        asof = args.asof
    else:
        hs = json.load(open(CACHE_DIR / "_hs300.json"))
        asof = (hs["k"] if isinstance(hs, dict) else hs)[-1][0]
    print(f"ASOF = {asof}    股票数 = {len(codes)}")

    # ---------- Pass 1 ----------
    recs, skip = [], Counter()
    done = 0
    jobs = [(c, asof) for c in codes]
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as ex:
        for code, rec, err in ex.map(_worker, jobs, chunksize=64):
            done += 1
            if done % 1000 == 0:
                print(f"  Pass1 {done}/{len(codes)}  ({time.time()-t0:.0f}s)", flush=True)
            if rec is None:
                skip[err or "unknown"] += 1
            else:
                recs.append(rec)
    print(f"Pass1 完成：有效 {len(recs)} / {len(codes)}，跳过 {dict(skip)}  ({time.time()-t0:.0f}s)")

    if not recs:
        print("❌ 没有可算的股票")
        return 2

    # ---------- Pass 2 ----------
    X = xsec.build_xsec(recs)
    cfg = config.raw()
    finals = [scoring.finalize(r, X) for r in recs]
    xsec.assign_ranks(finals, cfg)

    names = load_names()
    for f in finals:
        f["name"] = names.get(f["code"], "")
        f["asof"] = asof

    # ---------- 坏率表 ----------
    print(f"构建坏率表… ({time.time()-t0:.0f}s)", flush=True)
    try:
        bt = badrate.build()
        print(f"  full: n={bt['full']['n']} 基准坏率 {bt['full']['base_bad_rate']}% "
              f"AUC {bt['full']['auc']}  Q1..Q5 {[round(x,2) for x in bt['full']['quintiles']]}")
        print(f"  oos : n={bt['oos']['n']} 基准坏率 {bt['oos']['base_bad_rate']}% "
              f"AUC {bt['oos']['auc']}  Q1..Q5 {[round(x,2) for x in bt['oos']['quintiles']]}")
    except Exception as e:
        print(f"  ⚠️ 坏率表构建失败（不阻断）: {type(e).__name__}: {e}")
        bt = {}

    for f in finals:
        f["badrate"] = badrate.lookup(bt, f["core_score"], "oos") if bt else None

    # ---------- 落盘 ----------
    out_dir = Path(args.out) if args.out else SNAPSHOT_DIR / asof
    out_dir.mkdir(parents=True, exist_ok=True)

    with gzip.open(out_dir / "scores.jsonl.gz", "wt", encoding="utf-8") as fh:
        for f in finals:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")

    band_dist = dict(Counter(f["band"] for f in finals))
    covs = [f["core_coverage_pct"] for f in finals]
    meta = {
        "asof": asof,
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "universe_size": len(codes),
        "n_scored": len(finals),
        "n_skipped": len(codes) - len(finals),
        "skip_reasons": dict(skip),
        "band_distribution": band_dist,
        "bands": {"buy_pctl": config.buy_pctl(), "watch_pctl": config.watch_pctl()},
        "min_core_coverage": config.min_core_coverage(),
        "coverage": {
            "median_core_coverage_pct": round(sorted(covs)[len(covs) // 2], 1),
            "pct_at_100": round(sum(1 for c in covs if c >= 100) / len(covs) * 100, 1),
            "pct_below_min": round(sum(1 for c in covs if c < config.min_core_coverage()) / len(covs) * 100, 1),
        },
        "core_score": {
            "distinct_values": len({f["core_score"] for f in finals}),
            "min": min(f["core_score"] for f in finals),
            "median": round(sorted(f["core_score"] for f in finals)[len(finals) // 2], 2),
            "max": max(f["core_score"] for f in finals),
        },
        "flags": dict(Counter(fl for f in finals for fl in f["flags"])),
        "soft_demote": dict(Counter(s for f in finals for s in f["soft_demote"])),
        "unavailable_books": dict(Counter(
            b for f in finals for b, ok in f["book_available"].items() if not ok)),
        "core_books": list(book_rules.CORE_BOOKS),
        "consensus_books": list(book_rules.CONSENSUS_BOOKS),
        "config_hash": config.config_hash(),
    }
    (out_dir / "snapshot_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "badrate_table.json").write_text(
        json.dumps(bt, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 快照已写入 {out_dir}")
    print(f"   {len(finals)} 只   判定分布 {band_dist}")
    print(f"   核心分不同取值 {meta['core_score']['distinct_values']} 个"
          f"（min {meta['core_score']['min']} / 中位 {meta['core_score']['median']} / max {meta['core_score']['max']}）")
    print(f"   核心覆盖率中位 {meta['coverage']['median_core_coverage_pct']}%"
          f"，满覆盖 {meta['coverage']['pct_at_100']}%"
          f"，低于阈值 {meta['coverage']['pct_below_min']}%")
    print(f"   标注 {meta['flags']}   降级 {meta['soft_demote']}")
    print(f"   耗时 {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
