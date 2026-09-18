"""核心分历史轨迹 —— 从回测面板还原每只股票过去 6 年的分数走势。

为什么值得做：单看一个分数（60.5）无法回答「现在的情况」里的关键问题 ——
**这个分数相对它自己的历史是高还是低**。面板有 77 期月度快照，
且每期的核心分是同一套规则算的（parity 已验证），所以轨迹是可比的。

两个量：
  - `s` 原始核心分（0-100，绝对量，跨期可比）
  - `p` 当期横截面分位（0-100）—— 因为 band 是按**当期分位**定的，
        所以只有它才能回答「那时算不算 BUY」

注意：分位必须逐期重算。用今天的分位去回看历史会犯「用未来信息」的错。
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from . import book_rules

HISTORY_FILE = "history.json.gz"


def build(panel_path):
    """从 bt_robust_data.pkl 构建全市场历史轨迹。返回可 JSON 序列化的 dict。"""
    import pickle

    import numpy as np

    with open(panel_path, "rb") as fh:
        P = pickle.load(fh)
    books = list(P["books"])
    idx = [books.index(b) for b in book_rules.CORE_BOOKS]

    dates = [str(d) for d in P["dates"]]
    out = {}
    for di, d in enumerate(P["data"]):
        comp = d["S"][:, idx].mean(axis=1)
        codes = list(d["codes"])
        ok = ~np.isnan(comp)
        vals = comp[ok]
        order = np.argsort(vals, kind="mergesort")
        # 逐期分位（下界口径，与 scoring.percentile_rank 一致）
        ranks = np.empty(len(vals), dtype=float)
        ranks[order] = np.arange(len(vals))
        # 并列取平均秩，避免同一分数的人分位不同
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            if j > i:
                avg = (i + j) / 2.0
                ranks[order[i:j + 1]] = avg
            i = j + 1
        pctl = ranks / max(len(vals), 1) * 100

        codes_ok = [c for c, o in zip(codes, ok) if o]
        for c, s, p in zip(codes_ok, vals, pctl):
            rec = out.setdefault(c, {"s": [], "p": []})
            rec["s"].append(round(float(s), 1))
            rec["p"].append(round(float(p), 1))
    return {"dates": dates, "codes": out}


def write(snap_dir, panel_path):
    """写入快照目录。返回 (路径, 股票数)。"""
    data = build(panel_path)
    p = Path(snap_dir) / HISTORY_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    return p, len(data["codes"])


def load(snap_dir):
    p = Path(snap_dir) / HISTORY_FILE
    if not p.exists():
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def series(hist, code, current=None):
    """取单只股票的轨迹。

    `current` 为当前快照点 (asof, core_score, core_pctl)，会追加到末尾 ——
    面板最后一期是 2026-07-31，而快照是 2026-09-16，中间差一个多月。
    """
    if not hist:
        return None
    rec = (hist.get("codes") or {}).get(code)
    dates = list(hist.get("dates") or [])
    pts = []
    if rec:
        for d, s, p in zip(dates, rec["s"], rec["p"]):
            pts.append({"date": d, "core_score": s, "pctl": p, "source": "panel"})
    if current:
        asof, cs, cp = current
        if cs is not None and (not pts or pts[-1]["date"] < asof):
            pts.append({"date": asof, "core_score": cs,
                        "pctl": cp, "source": "snapshot"})
    if not pts:
        return None
    sc = [x["core_score"] for x in pts]
    return {
        "points": pts,
        "n": len(pts),
        "min": min(sc), "max": max(sc),
        "first": pts[0], "last": pts[-1],
        "delta": round(pts[-1]["core_score"] - pts[0]["core_score"], 1),
        "pctl_now": pts[-1]["pctl"],
        "pctl_median": sorted(x["pctl"] for x in pts)[len(pts) // 2],
    }
