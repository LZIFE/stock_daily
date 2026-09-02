#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""唐朝·财报排雷
核心: 毛利率/ROE/净利同比/营收同比 一票否决排雷
"""


def score(r, ctx):
    gm = r.get("gm") or 0.0
    roe = r.get("roe") or 0.0
    np_yoy = r.get("np_yoy") or 0.0
    rev_yoy = r.get("rev_yoy") or 0.0
    s = 50.0
    # 毛利率 唐朝 40%+
    if gm >= 40:
        s += 15
    elif gm >= 25:
        s += 8
    elif gm < 12:
        s -= 15
    # ROE
    if roe >= 15:
        s += 12
    elif roe >= 10:
        s += 5
    elif roe < 5:
        s -= 10
    # 净利连续性 (近似: 当年同比为正+营收正)
    if np_yoy > 0 and rev_yoy > 0:
        s += 10
    elif np_yoy < 0 and rev_yoy < 0:
        s -= 18
    elif np_yoy < 0:
        s -= 8
    return s
