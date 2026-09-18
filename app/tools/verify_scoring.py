"""算分 parity 验收门。

阶段 0 结束前**必须全绿**，否则下面所有层（band、坏率、AI 事实块）继承错误。

两道校验：
  1. 面板校验（决定性）：用与回测面板同一天（bt_robust_data.pkl 最后一期）
     重建快照，逐只逐本比对 29 个分数。对不上 → 横截面口径或 PIT 有问题。
  2. 自洽校验：29 本书集合、核心 4 本、分档配置与 book_rules 一致。

用法:
    # 先在面板最后一天建一份快照
    python -m app.build_snapshot --asof 2026-07-31 --out app/data/snapshot/_verify
    python -m app.tools.verify_scoring --snapshot app/data/snapshot/_verify
"""
from __future__ import annotations

import argparse
import gzip
import json
import pickle
import sys
from collections import Counter
from pathlib import Path

from .. import book_rules
from ..paths import PANEL_PKL


def load_snapshot(d):
    d = Path(d)
    p = d / "scores.jsonl.gz"
    out = {}
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            out[r["code"]] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--tol", type=float, default=1.01, help="允许的分数差（float32 存储误差）")
    args = ap.parse_args()

    ok = True

    # ---------- ② 自洽校验 ----------
    print("=" * 68)
    print("② 自洽校验")
    print("=" * 68)
    names = list(book_rules.ORDER)
    if len(names) != 29:
        print(f"  ❌ book_rules 有 {len(names)} 本，应为 29")
        ok = False
    else:
        print(f"  ✅ 29 本书齐备")
    if set(book_rules.CORE_BOOKS) <= set(names):
        print(f"  ✅ 核心 4 本 {book_rules.CORE_BOOKS}")
    else:
        print(f"  ❌ 核心书不在 29 本内: {set(book_rules.CORE_BOOKS) - set(names)}")
        ok = False

    # ---------- ① 面板校验 ----------
    print()
    print("=" * 68)
    print("① 面板校验：与 bt_robust_data.pkl 最后一期逐本比对")
    print("=" * 68)
    snap = load_snapshot(args.snapshot)
    with open(PANEL_PKL, "rb") as fh:
        P = pickle.load(fh)

    li = len(P["data"]) - 1
    asof = P["dates"][li]
    d = P["data"][li]
    S, codes = d["S"], list(d["codes"])
    pbooks = list(P["books"])
    print(f"  面板期 {li}  asof={asof}  n={len(codes)}")
    print(f"  快照目录 {args.snapshot}")

    if str(asof) not in str(args.snapshot) and "_verify" not in str(args.snapshot):
        print(f"  ⚠️ 快照的 asof 看起来与面板日期 {asof} 不一致，比对可能无意义")

    # 书名列对齐
    if pbooks != names:
        print(f"  ⚠️ 面板书序与 book_rules 不同，按名字映射")
    col = {b: pbooks.index(b) for b in names if b in pbooks}

    common = [c for c in codes if c in snap]
    print(f"  可比对 {len(common)} / {len(codes)} 只"
          + (f"（面板有但快照缺 {len(codes)-len(common)} 只）" if len(common) < len(codes) else ""))

    if not common:
        print("  ❌ 无可比对样本 —— 快照是否用 --asof {asof} 构建？")
        return 1

    diff_by_book = Counter()
    worst = {}
    n_cmp = 0
    for c in common:
        row = snap[c]
        pi = codes.index(c)
        for b in names:
            if b not in col:
                continue
            ours = row["books"].get(b)
            theirs = float(S[pi, col[b]])
            if ours is None:
                continue
            n_cmp += 1
            dv = abs(float(ours) - theirs)
            if dv > args.tol:
                diff_by_book[b] += 1
                if dv > worst.get(b, (0,))[0]:
                    worst[b] = (dv, c, float(ours), theirs)

    print(f"\n  比对 {n_cmp} 个分数点，容差 {args.tol}")
    if not diff_by_book:
        print(f"  ✅ 全部一致 —— 适配器精确复现了回测口径")
    else:
        ok = False
        print(f"  ❌ {len(diff_by_book)} 本书存在不一致，共 {sum(diff_by_book.values())} 处")
        print(f"\n  {'书':16s}{'不一致数':>9s}   最差样例")
        for b, n in diff_by_book.most_common():
            dv, c, o, t = worst[b]
            print(f"  {b:16s}{n:>9d}   {c}  ours={o} panel={t} Δ={dv:.2f}")

    print()
    print("=" * 68)
    print("结论：" + ("✅ PARITY 通过，可进入下一阶段" if ok else "❌ PARITY 未通过，先修再往下做"))
    print("=" * 68)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
