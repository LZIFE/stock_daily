#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""利弗莫尔·趋势金字塔
核心: 突破 + 趋势起点 + 顺势
"""


def score(r, ctx):
    v60 = r.get("vs_ma60")
    chg5 = r.get("chg5") or 0.0
    chg_today = r.get("chg_today") or 0.0
    pos = r.get("pos60") or 50.0
    s = 50.0
    # 趋势起点: 站上MA60 + 5日温和涨
    if v60 is not None and v60 > 0 and 3 <= chg5 <= 12:
        s += 22
    elif v60 is not None and v60 > 0:
        s += 8
    elif v60 is not None and v60 < -5:
        s -= 18
    # 当日强度
    if chg_today >= 2:
        s += 8
    elif chg_today < -3:
        s -= 12
    # 位置 40-70 是利弗莫尔的"甜区"
    if 40 <= pos <= 70:
        s += 10
    elif pos >= 85:
        s -= 10
    return s
