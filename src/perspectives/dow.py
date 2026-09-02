#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""道氏理论 (兼容)"""


def score(r, ctx):
    v60 = r.get("vs_ma60")
    if v60 is None:
        return 50.0
    if v60 > 5:
        return 75.0
    if v60 > 0:
        return 60.0
    if v60 > -5:
        return 45.0
    return 30.0
