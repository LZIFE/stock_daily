#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""邱国鹭 · 便宜且不拥挤（v2 核心分 40%）

规则来源：bt_scorer.books9_new 的「邱国鹭」分支，逐项对齐以保持与回测口径一致。
为什么它是核心分权重最高的一本：在《作者思想有效性与稳健权重_报告.md》里，
它是唯一「独立超额与边际贡献在两个持有周期同时为正」的选股书——
mc60 +1.506 / mc250 +1.266，60 日 OOS 超额 +1.13pp（29 本里唯一胜率 >50%），
Bull/Neutral/Defensive 三状态全为正，回撤 −16.9% 是基本面层最小。

一句话：低 PE + 低 PB + 不拥挤（成交额分位低）+ 低负债。

⚠️ 数据缺口（当前生产数据源没有；缺失时该项自动跳过，与 bt_scorer 的 `if x and ...` 行为一致）：
    pb        市净率        —— 需在 fetcher.load_pool 或财务源补充
    debt      资产负债率    —— 同上
    quality_bad 财报异常标记 —— 需唐朝模块产出
    ctx["amt_pct"] 成交额分位（拥挤度代理）—— 由 score_v2 横截面计算后注入
"""


def score(r, ctx):
    ctx = ctx or {}
    pe = r.get("pe_now")
    pb = r.get("pb")
    debt = r.get("debt")
    qb = r.get("quality_bad")
    amt_pct = ctx.get("amt_pct")          # 拥挤度代理：成交额全市场分位

    s = 50.0
    if pe and pe < 15:
        s += 20
    elif pe and pe < 25:
        s += 8
    if pb and pb < 2:
        s += 12
    elif pb and pb > 5:
        s -= 12
    if amt_pct is not None:
        if amt_pct > 85:
            s -= 15                        # 数月亮不数星星：拥挤
        elif amt_pct < 40:
            s += 8
    if debt and debt < 40:
        s += 8
    if qb:
        s -= 15
    return max(0.0, min(100.0, s))
