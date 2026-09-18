#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蜡烛图 · K线（v2 核心分 24.7%）

规则来源：bt_scorer.books20 的「蜡烛图·K线」分支。
原实现用的是「近 5 日阳线数」，本文件原为另一套简化规则（用 chg_today / pos60），
v2 改为与回测口径对齐——否则回测里 mc60 +0.529 / mc250 +0.476 的证据不适用。

它是第二个「强」：60 日 OOS 超额 +1.41pp、250 日 +7.18pp，两周期边际贡献均 >0.4。
值得注意的是：本窗口可重复的信息更多来自**微观结构（量价形态）**，而不是宏大叙事。

依赖 r["yang5"]（近 5 日阳线数），由 fetcher.calc_tech 提供。
"""


def score(r, ctx):
    yang5 = r.get("yang5")
    if yang5 is None:
        return 50.0
    s = 50.0
    if yang5 >= 4:
        s += 25
    elif yang5 >= 3:
        s += 15
    elif yang5 <= 1:
        s -= 15
    return max(0.0, min(100.0, s))
