#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""芒格·避开愚蠢
核心: 不在高估+烂生意+高波动+亏损的股票上买 (反向清单)
"""


def score(r, ctx):
    pe = r.get("pe_now")
    roe = r.get("roe") or 0.0
    gm = r.get("gm") or 0.0
    np_yoy = r.get("np_yoy") or 0.0
    s = 70.0  # 默认"避免"=高分(代表反向)
    # 烂生意特征 → 减分
    if gm < 20:
        s -= 15
    if roe < 8:
        s -= 12
    if np_yoy < 0:
        s -= 15
    if pe is not None and pe > 40:
        s -= 12
    # 好生意 → 加分
    if gm >= 35 and roe >= 15 and np_yoy > 0:
        s += 10
    return s
