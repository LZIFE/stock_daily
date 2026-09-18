#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""买入决策评分引擎 v2

与 v1 (score_engine.py) 的区别：
    v1  门禁 + 量价50/价值30/心理20 加权 + 仓位层，输出一个总分
    v2  门禁 + 核心分(4本) / 共识分 / 分歧度 + 仓位层，输出三态判定

设计依据见 SCORING_V2.md；权重与门禁参数见 config/score_weights_v2.json。

为什么改：
  1. v1 的 12 个加权视角里，有 5 个在《作者思想有效性与稳健权重_报告.md》中
     边际贡献为负（合计占 47/100 分）；而全项目唯一两周期边际贡献都为正的
     两本书（邱国鹭、蜡烛图）权重为 0。
  2. 「买不买」是分类问题（只要尾部准），不是排序问题——评价方式不同。
  3. 阈值 75/60 无依据；改用核心分的全市场分位标定。

用法:
    from score_v2 import evaluate_pool
    results = evaluate_pool(pool_rows, ctx={"hwm_drawdown_pct": 0})
"""
import json
import os

import perspectives as P

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "score_weights_v2.json")

# 核心分 4 本书各自需要的字段（用于计算覆盖率与数据缺口）
CORE_FIELDS = {
    "coulling": ["pe_now", "pb", "amt_pct", "debt", "quality_bad"],
    "candlestick": ["yang5"],
    "buffett": ["ocf_ttm", "np_ttm", "roe", "pe_now", "debt"],
    "shefrin": ["amp60"],
}


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _pctl(sorted_vals, v):
    """升序列表中的百分位（0-100）"""
    if not sorted_vals or v is None:
        return None
    lo, hi = 0, len(sorted_vals)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_vals[mid] < v:
            lo = mid + 1
        else:
            hi = mid
    return lo / len(sorted_vals) * 100


def _coverage(r, ctx):
    """核心分字段覆盖率 + 缺口清单。

    缺失字段不能用 50 分兜底——那是把「不知道」伪装成「中性」。
    """
    need = set()
    for flds in CORE_FIELDS.values():
        need.update(flds)
    missing = []
    for f in sorted(need):
        v = ctx.get(f) if f == "amt_pct" else r.get(f)
        if v is None:
            missing.append(f)
    cov = (len(need) - len(missing)) / len(need) * 100
    return round(cov, 1), missing


def _gates(r, cfg, ctx):
    """L0 门禁：返回 (否决, 降级, 冻结, 原因列表)"""
    hard, soft, freeze, why = [], [], [], []
    rules = cfg["veto_rules"]

    # 流动性（否决）
    floor = 5e7
    if r.get("amt20") is not None and r["amt20"] < floor:
        hard.append("流动性不足")
        why.append(f"20日均成交额 {r['amt20']/1e4:.0f}万 < {floor/1e4:.0f}万")

    # 财务可信（否决）—— 数据源缺年报序列，规则未实现
    if not rules["financial_unreliable"].get("available"):
        pass

    # 估值极端（降级）
    if r.get("pe_pctl") is not None and r["pe_pctl"] > 95:
        soft.append("估值极端")
        why.append(f"PE {r.get('pe_now')} 全市场 {r['pe_pctl']:.0f} 分位")

    # 拥挤度（降级）
    if r.get("amt_pctl") is not None and r["amt_pctl"] > 90:
        soft.append("交易拥挤")
        why.append(f"成交额 {r['amt_pctl']:.0f} 分位 > 90")

    # 账户纪律（冻结）
    dd = ctx.get("hwm_drawdown_pct") or 0.0
    if dd > 20:
        freeze.append("HWM 回撤冻结")
        why.append(f"账户 HWM 回撤 {dd:.1f}% 冻结买入")

    return hard, soft, freeze, why


def _position_cap(r, cfg, ctx):
    """L2 仓位层：决定「买多少」，不决定「买不买」"""
    pl = cfg["position_layer"]
    st = ctx.get("regime") or "neutral"
    base = pl["regime"].get(f"state_{st}", pl["regime"]["state_neutral"]) / 100.0

    volat = r.get("volat")
    if volat and volat > 0:
        vt = min(pl["vol_target"]["max_single_pct"] / 100.0,
                 (pl["vol_target"]["target_vol_pct"] / volat))
        vt = max(vt, pl["vol_target"]["min_single_pct"] / 100.0)
    else:
        vt = pl["vol_target"]["max_single_pct"] / 100.0

    dd = ctx.get("hwm_drawdown_pct") or 0.0
    hm = pl["hwm_multiplier"]
    mult = (hm["under_5pct"] if dd < 5 else hm["5_to_10pct"] if dd < 10
            else hm["10_to_20pct"] if dd < 20 else hm["over_20pct"])

    return round(base * vt * mult * 100, 2), f"regime={st} × 波动率目标 × HWM {dd:.0f}%"


def evaluate_pool(rows, ctx=None):
    """对一批股票打分。

    rows: fetcher.fetch_pool() 的输出（含 calc_tech 的技术字段）
    ctx : {"hwm_drawdown_pct": float, "regime": "attack|neutral|protect|defend"}
    """
    cfg = _load_config()
    ctx = dict(ctx or {})
    ok = [r for r in rows if not r.get("error")]
    if not ok:
        return []

    # 横截面分位（在当日全池内计算，与回测口径一致）
    amts = sorted([r["amt20"] for r in ok if r.get("amt20") is not None])
    pes = sorted([r["pe_now"] for r in ok
                  if r.get("pe_now") is not None and r["pe_now"] > 0])

    out = []
    for r in ok:
        c = dict(ctx)
        c["amt_pct"] = _pctl(amts, r.get("amt20"))
        r["amt_pctl"] = c["amt_pct"]
        r["pe_pctl"] = _pctl(pes, r.get("pe_now") if (r.get("pe_now") or 0) > 0 else None)

        scores = P.score_all(r, c)
        cw = cfg["core_score"]["perspectives"]
        core = sum(scores.get(k, 50.0) * w for k, w in cw.items()) / sum(cw.values())

        ex = set(cfg["consensus_score"]["exclude"])
        mods = [m for m in P.CONSENSUS_MODULES if m not in ex]
        cons = sum(scores.get(m, 50.0) for m in mods) / len(mods)

        cov, missing = _coverage(r, c)
        hard, soft, freeze, why = _gates(r, cfg, c)
        cap, cap_reason = _position_cap(r, cfg, c)

        out.append({
            "code": r.get("code"), "name": r.get("name"), "close": r.get("close"),
            "core": round(core, 1), "cons": round(cons, 1),
            "div": round(core - cons, 1),
            "coverage": cov, "missing_fields": missing,
            "hard_veto": hard, "soft_demote": soft, "freeze": freeze,
            "reasons": why, "position_cap_pct": cap, "position_reason": cap_reason,
            "components": {k: round(v, 1) for k, v in scores.items()},
        })

    # 三态判定：按核心分在全池的分位标定（不写死绝对分数）
    valid = sorted([x["core"] for x in out if not x["hard_veto"]
                    and not x["freeze"]
                    and x["coverage"] >= cfg["coverage"]["min_coverage_pct"]])
    for x in out:
        if x["freeze"]:
            x["band"], x["core_pctl"] = "FROZEN", None
            continue
        if x["hard_veto"]:
            x["band"], x["core_pctl"] = "EXCLUDED", None
            continue
        if x["coverage"] < cfg["coverage"]["min_coverage_pct"]:
            x["band"], x["core_pctl"] = "NO_DATA", None
            continue
        p = _pctl(valid, x["core"])
        x["core_pctl"] = round(p, 1) if p is not None else None
        if x["soft_demote"]:
            x["band"] = "WATCH"
        elif p is not None and p >= cfg["bands"]["buy_pctl"]:
            x["band"] = "BUY"
        elif p is not None and p >= cfg["bands"]["watch_pctl"]:
            x["band"] = "WATCH"
        else:
            x["band"] = "AVOID"
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetcher import fetch_pool, load_pool
    res = evaluate_pool(fetch_pool(load_pool()), {"hwm_drawdown_pct": 0})
    for x in sorted(res, key=lambda a: -a["core"])[:20]:
        print(f"{x['code']:8s}{x['name'][:8]:10s}{x['band']:9s}"
              f"核心{x['core']:>6.1f} 共识{x['cons']:>6.1f} 分歧{x['div']:>6.1f} "
              f"覆盖{x['coverage']:>5.1f}% 仓位{x['position_cap_pct']:>5.1f}%")
    from collections import Counter
    print()
    print("判定分布:", dict(Counter(x["band"] for x in res)))
    gaps = Counter(f for x in res for f in x["missing_fields"])
    print("数据缺口字段:", dict(gaps))
