#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""达利欧 · 风险平价（v2 核心分）

规则来源：bt_scorer.books9_new 的「达利欧」分支，逐项对齐。
核心是**低波动优先** + 趋势不为负 + 宏观防御（低负债）。

为什么进核心分：在分类目标（坏结果 = 未来 60 日绝对收益 < −20%）上，
单本 Q1−Q5 = **12.39pp**、AUC **0.6162**，排第 3 —— 比它在 mc（排序目标）
上的表现好得多（mc60 +0.298 / mc250 −0.0）。这正是「排序力 ≠ 分类力」的例子。

⚠️ 数据缺口（缺失时该项自动跳过）：
    debt 资产负债率 —— 当前数据源没有
    ctx["vol_pct"] 波动率全市场分位 —— 由 score_v2 横截面计算后注入
"""


def score(r, ctx):
    ctx = ctx or {}
    volat = r.get("volat")
    pct_vol = ctx.get("vol_pct")
    ma60 = r.get("ma60")
    price = r.get("close")
    debt = r.get("debt")

    s = 50.0
    if volat is not None and pct_vol is not None:
        if pct_vol < 20:
            s += 25
        elif pct_vol < 40:
            s += 12
        elif pct_vol > 80:
            s -= 15
    if ma60 and price and price >= ma60 * 0.95:
        s += 10
    if debt and debt < 50:
        s += 8
    return max(0.0, min(100.0, s))
