#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日本蜡烛图 (兼容, 简化)"""


def score(r, ctx):
    chg_today = r.get("chg_today") or 0.0
    pos = r.get("pos60") or 50.0
    s = 50.0
    if -2 <= chg_today <= 2 and pos <= 50:
        s += 12   # 区间内小实体,可能孕育反转
    if chg_today > 5:
        s -= 5    # 大阳线后买风险
    if chg_today < -5:
        s += 8    # 长下影/急跌后买点信号
    return s
