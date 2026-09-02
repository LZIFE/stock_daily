#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""爱德华兹-麦吉·趋势形态
核心: MA20/MA60/60日位置/趋势方向
"""


def score(r, ctx):
    v20 = r.get("vs_ma20")
    v60 = r.get("vs_ma60")
    pos = r.get("pos60") or 50.0
    s = 50.0
    if v60 is not None:
        if v60 >= 5:
            s += 20      # 站上MA60且超5%
        elif v60 >= 0:
            s += 12
        elif v60 >= -5:
            s += 4
        else:
            s -= 12
    if v20 is not None:
        if -3 <= v20 <= 1.5:
            s += 12      # 回踩MA20企稳
        elif v20 > 1.5:
            s -= 5       # 偏离
        elif v20 < -7:
            s -= 12
    if pos <= 30:
        s += 8
    elif pos >= 80:
        s -= 12
    return s
