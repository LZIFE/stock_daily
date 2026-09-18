#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""格雷厄姆 · 安全边际（v2 核心分）

规则来源：bt_scorer.books20 的「格雷厄姆」分支——**便宜 + 低负债**。

⚠️ 本文件原实现用的是另一套规则（PE 分档 + ROE + 净利同比），与回测口径不一致，
   因此回测里那套分类证据（单本 Q1−Q5 13.44pp / AUC 0.6318，29 本里最高）**不适用**。
   已按 bt_scorer 口径对齐。原实现的效果未经验证。

为什么进核心分：分类目标上它是单本第一（Q1−Q5 13.44pp，AUC 0.6318）。
注意这与 mc（排序目标）的结论不同——格雷厄姆的 mc60 只有 +0.203、mc250 为 0。

⚠️ 数据缺口（缺失时该项自动跳过）：
    pb 市净率 —— 当前数据源没有，而它在本规则里占 +15/−15，是重要一项
"""


def score(r, ctx):
    pe = r.get("pe_now")
    pb = r.get("pb")

    s = 50.0
    if pe and pe < 15:
        s += 25
    elif pe and pe < 25:
        s += 10
    elif pe and pe > 60:
        s -= 20
    if pb and pb < 1.5:
        s += 15
    elif pb and pb < 3:
        s += 5
    elif pb and pb > 6:
        s -= 15
    return max(0.0, min(100.0, s))
