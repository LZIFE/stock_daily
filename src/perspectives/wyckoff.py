#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""威科夫量价·资金驱动
核心: 量比+成交额确认(吸筹)
输入: vol_ratio, chg5, chg_today, pos60
输出: 0-100
"""


def score(r, ctx):
    vr = r.get("vol_ratio") or 1.0
    chg5 = r.get("chg5") or 0.0
    pos = r.get("pos60") or 50.0
    # 吸筹特征: 量大 + 价未大涨 + 位置不极端
    s = 50.0
    if 1.2 <= vr <= 2.5:
        s += 15  # 健康放量
    elif vr > 2.5:
        s += 5   # 异常放量(可能见顶)
    if 0 <= chg5 <= 8:
        s += 15  # 5日温和涨,典型吸筹
    elif chg5 > 15:
        s -= 10  # 急涨,可能赶顶
    if pos <= 60:
        s += 10  # 60日区间中下,资金在低吸
    elif pos >= 85:
        s -= 10
    return s
