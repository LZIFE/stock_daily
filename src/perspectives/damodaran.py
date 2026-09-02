#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""达摩达兰·估值三要素
核心: 现金流(净利同比) + 增长率(营收同比) + 风险(PE合理性)
"""


def score(r, ctx):
    np_yoy = r.get("np_yoy") or 0.0
    rev_yoy = r.get("rev_yoy") or 0.0
    pe = r.get("pe_now")
    s = 50.0
    # 增长率
    if rev_yoy >= 20:
        s += 18
    elif rev_yoy >= 10:
        s += 10
    elif rev_yoy < 0:
        s -= 15
    # 净利印证
    if np_yoy >= 30:
        s += 10
    elif np_yoy < 0:
        s -= 10
    # PE 合理性
    if pe is not None and pe > 0:
        if pe <= 12:
            s += 12
        elif pe <= 22:
            s += 6
        elif pe <= 35:
            s -= 4
        else:
            s -= 14
    return s
