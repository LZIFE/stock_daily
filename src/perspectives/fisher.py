#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""费雪·成长股
核心: 营收增速 持续 + 净利印证 + 高毛利护城河
"""


def score(r, ctx):
    rev_yoy = r.get("rev_yoy") or 0.0
    np_yoy = r.get("np_yoy") or 0.0
    gm = r.get("gm") or 0.0
    s = 50.0
    if rev_yoy >= 25:
        s += 22
    elif rev_yoy >= 15:
        s += 14
    elif rev_yoy >= 8:
        s += 5
    else:
        s -= 10
    if np_yoy >= rev_yoy:
        s += 10  # 净利增速 ≥ 营收增速 (质量)
    elif np_yoy < 0:
        s -= 12
    if gm >= 35:
        s += 8
    elif gm < 20:
        s -= 5
    return s
