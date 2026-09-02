#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""霍华德马克斯·周期温度
核心: 大盘温度(指数涨跌) + 个股位置 → 不在极端时给分
"""


def score(r, ctx):
    pos = r.get("pos60") or 50.0
    bench = ctx.get("bench_chg_today") or 0.0
    s = 50.0
    # 大盘温度反向: 大盘狂涨时该谨慎
    if bench > 2:
        s -= 15
    elif bench > 1:
        s -= 5
    elif bench < -1.5:
        s += 12   # 大盘恐慌时是好买点
    elif bench < -0.5:
        s += 5
    # 个股位置: 中段最佳
    if 30 <= pos <= 70:
        s += 12
    elif pos >= 85:
        s -= 12
    elif pos <= 15:
        s += 5
    return s
