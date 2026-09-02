#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正帆·三阶段+产业
核心: 成交额跃迁 + 产业逻辑(净利增速/营收增速)
"""


def score(r, ctx):
    vr = r.get("vol_ratio") or 1.0
    np_yoy = r.get("np_yoy") or 0.0
    rev_yoy = r.get("rev_yoy") or 0.0
    pos = r.get("pos60") or 50.0
    s = 50.0
    # 成交额跃迁: 量比>1.5 + 价格未暴涨
    chg5 = r.get("chg5") or 0.0
    if 1.3 <= vr <= 2.2 and chg5 < 10:
        s += 18
    elif vr > 2.5 and chg5 > 12:
        s -= 8
    # 产业逻辑: 营收+净利双高增
    if rev_yoy >= 15 and np_yoy >= 20:
        s += 15
    elif rev_yoy >= 0 and np_yoy >= 0:
        s += 5
    elif np_yoy < 0:
        s -= 15
    if pos <= 50:
        s += 5
    return s
