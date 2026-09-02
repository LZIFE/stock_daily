#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卡尼曼·冲动抑制
核心: 抑制 FOMO/过度自信, 大涨后给低分
"""


def score(r, ctx):
    chg5 = r.get("chg5") or 0.0
    chg_today = r.get("chg_today") or 0.0
    pos = r.get("pos60") or 50.0
    s = 50.0
    # 5日涨超 15% → 损失厌恶/锚定风险高
    if chg5 > 20:
        s -= 18
    elif chg5 > 12:
        s -= 10
    elif 0 <= chg5 <= 8:
        s += 10
    elif chg5 < -10:
        s -= 8    # 恐慌中买也是偏差
    # 当日大涨
    if chg_today > 7:
        s -= 8
    elif chg_today > 4:
        s -= 3
    # 高位 = 易锚定
    if pos >= 85:
        s -= 8
    return s
