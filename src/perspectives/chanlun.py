#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缠论·中枢背驰 (简化版: 基于 MA 距离判定)
核心: MA20 与 MA60 的关系=中枢, vs_ma20 偏离度=背驰近似
"""


def score(r, ctx):
    v20 = r.get("vs_ma20")
    v60 = r.get("vs_ma60")
    chg_today = r.get("chg_today") or 0.0
    s = 50.0
    if v20 is None or v60 is None:
        return 50.0
    # MA20 > MA60: 多头中枢雏形
    if v60 > 0 and -3 <= v20 <= 1.5:
        s += 18  # 趋势中回踩买点
    elif v60 > 0 and v20 > 5:
        s -= 8   # 远离中枢
    elif v60 < -3:
        s -= 12  # 趋势破坏
    # 当日强度
    if chg_today >= 2 and -2 <= v20 <= 2:
        s += 12
    return s
