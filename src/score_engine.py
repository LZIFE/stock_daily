#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多视角评分引擎
输入: 单只股票 dict (r) + 市场上下文 (ctx)
输出: {total, components: {name: score}, veto: [], band: 'A'/'B'/'danger'/'watch'}

三层:
  第0层 硬否决: 财报/估值/狂热/HWM
  第1层 信号层: 量价50% + 价值30% + 心理纪律20% 加权
  第2层 仓位层: 市场状态 + HWM 决定最大建仓比例
"""
import json
import os
import perspectives as P

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "score_weights.json")


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------- 第0层 硬否决 ----------
def _veto_check(r, cfg, ctx):
    """返回 (是否否决, 原因列表)"""
    reasons = []
    excluded = False
    demoted = False
    freeze = False
    np_yoy = r.get("np_yoy") or 0.0
    pe = r.get("pe_now")
    bench = ctx.get("bench_chg_today") or 0.0
    hwm_dd = ctx.get("hwm_drawdown_pct") or 0.0  # 0~100

    # 财报造假嫌疑 (唐朝): 连续亏损近似
    if np_yoy < -50:
        excluded = True
        reasons.append(f"净利同比 {np_yoy:.0f}% 异常亏损")
    # 安全边际: PE 极端
    if pe is not None and pe > 100:
        demoted = True
        reasons.append(f"PE {pe:.1f} 极端高估")
    # 市场极端狂热
    if bench > 2.5:
        demoted = True
        reasons.append(f"大盘 {bench:+.2f}% 极端狂热")
    # HWM 回撤 > 20% → 冻结买入
    if hwm_dd > 20:
        freeze = True
        reasons.append(f"账户 HWM 回撤 {hwm_dd:.1f}% 冻结买入")
    return excluded, demoted, freeze, reasons


# ---------- 第1层 信号层 ----------
def _signal_score(r, cfg, ctx):
    """返回 (加权总分, 组件分 dict)"""
    scores = P.score_all(r, ctx)
    sg = cfg["signal_groups"]
    total = 0.0
    components = {}
    for grp_name, grp in sg.items():
        grp_w = grp["weight_total"] / 100.0
        sub_total = 0.0
        sub_w_sum = sum(grp["perspectives"].values())
        for p_name, p_w in grp["perspectives"].items():
            p_w_norm = p_w / sub_w_sum  # 组内归一化
            s = scores.get(p_name, 50.0)
            sub_total += s * p_w_norm
            components[p_name] = round(s, 1)
        total += sub_total * grp_w
    # 制衡 (malkiel): 当价值类分 < 50 时,把总分压低 5%
    val_grp_avg = sum(scores.get(n, 50) for n in sg["value"]["perspectives"]) / len(sg["value"]["perspectives"])
    if val_grp_avg < 40:
        total *= 0.95
    return round(total, 1), components


# ---------- 第2层 仓位层 ----------
def _position_cap(r, cfg, ctx):
    """返回 (建议建仓比例 %, 原因)"""
    pl = cfg["position_layer"]
    bench = ctx.get("bench_chg_today") or 0.0
    hwm_dd = ctx.get("hwm_drawdown_pct") or 0.0
    # 市场状态
    if bench > 1:
        cap = pl["market_state_attack"] / 100.0
        state = "攻击"
    elif bench > -0.5:
        cap = pl["market_state_normal"] / 100.0
        state = "中性"
    elif bench > -1.5:
        cap = pl["market_state_protect"] / 100.0
        state = "保护"
    else:
        cap = pl["market_state_defend"] / 100.0
        state = "防守"
    # HWM 乘子
    if hwm_dd < 5:
        mult = pl["hwm_under_5pct"]
        dd = "<5%"
    elif hwm_dd < 10:
        mult = pl["hwm_5_to_10pct"]
        dd = "5-10%"
    elif hwm_dd < 20:
        mult = pl["hwm_10_to_20pct"]
        dd = "10-20%"
    else:
        mult = pl["hwm_over_20pct"]
        dd = ">20%冻结"
    return round(cap * mult * 100, 1), f"市场{state}({bench:+.2f}%) × HWM{dd}"


# ---------- 主入口 ----------
def evaluate(r, ctx=None):
    """对单只股票评分
    ctx 至少包含: bench_chg_today (大盘当日涨跌幅 %), hwm_drawdown_pct (账户回撤 0-100)
    """
    cfg = _load_config()
    ctx = ctx or {}
    excluded, demoted, freeze, veto_reasons = _veto_check(r, cfg, ctx)
    total, components = _signal_score(r, cfg, ctx)
    cap_pct, pos_reason = _position_cap(r, cfg, ctx)

    if freeze:
        band = "frozen"
    elif excluded:
        band = "excluded"
    elif demoted or total < cfg["tier_thresholds"]["watch"]:
        band = "watch"
    elif total < cfg["tier_thresholds"]["tier_a"]:
        band = "tier_b"
    else:
        band = "tier_a"

    return {
        "code": r.get("code"),
        "name": r.get("name"),
        "total": total,
        "band": band,
        "components": components,
        "veto": veto_reasons,
        "position_cap_pct": cap_pct,
        "position_reason": pos_reason,
    }


# ---------- 批量 ----------
def evaluate_pool(rows, ctx=None):
    return [evaluate(r, ctx) for r in rows if not r.get("error")]
