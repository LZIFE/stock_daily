#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""格雷厄姆·安全边际
核心: PE < 15 为便宜, ROE > 12% 为有质量, 净利同比非负
"""


def score(r, ctx):
    pe = r.get("pe_now")
    roe = r.get("roe") or 0.0
    np_yoy = r.get("np_yoy") or 0.0
    s = 50.0
    if pe is not None and pe > 0:
        if pe <= 8:
            s += 22
        elif pe <= 12:
            s += 15
        elif pe <= 18:
            s += 5
        elif pe <= 30:
            s -= 8
        else:
            s -= 18
    if roe >= 15:
        s += 10
    elif roe >= 10:
        s += 5
    elif roe < 5:
        s -= 10
    if np_yoy < 0:
        s -= 10
    return s
