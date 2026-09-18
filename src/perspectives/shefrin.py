#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""舍夫林 · 行为（v2 核心分 17.3%）

规则来源：bt_scorer.books20 的「舍夫林·行为」分支。
证据：mc60 +0.640（成立）/ mc250 +0.061（≈0），属「中」。

核心只有一件事：**低波动偏好**。行为金融的证据是投资者系统性高估高波动标的的收益，
因此「振幅小」本身就是一个可重复的正面信号。它在 Neutral 状态下最强（+2.14pp）。

依赖 r["amp60"]（60 日平均振幅 %），由 fetcher.calc_tech 提供。
"""


def score(r, ctx):
    amp60 = r.get("amp60")
    if amp60 is None:
        return 50.0
    s = 50.0
    if amp60 <= 4:
        s += 15
    elif amp60 > 8:
        s -= 15
    return max(0.0, min(100.0, s))
