#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""巴菲特 · 现金利润质量 + 便宜好生意（v2 核心分 18.0%）

规则来源：bt_scorer.books9_new 的「巴菲特」分支。
证据：mc60 +0.737（成立）/ mc250 −0.006（≈0），属「中」——只在一个持有周期提供独立增量。

核心是「利润是不是真的」：经营现金流 / 净利润 的比值。
>1.2 说明利润有现金支撑；<0.4 说明利润可能是纸面的。

⚠️ 数据缺口（当前生产数据源没有；缺失时自动跳过）：
    ocf_ttm 经营现金流(TTM)  —— 需财务源补充，这是本书的主项，缺它则本书退化
    np_ttm  归母净利(TTM)    —— 同上
    debt    资产负债率       —— 同上
    可用：roe、pe_now
"""


def score(r, ctx):
    pe = r.get("pe_now")
    roe = r.get("roe")
    debt = r.get("debt")
    ocf_ttm = r.get("ocf_ttm")
    np_ttm = r.get("np_ttm")

    s = 50.0
    # 主项：现金利润质量
    if ocf_ttm and np_ttm and np_ttm > 0:
        ratio = ocf_ttm / np_ttm
        if ratio > 1.2:
            s += 25
        elif ratio > 0.8:
            s += 10
        elif ratio < 0.4:
            s -= 20
    if roe and roe > 15:
        s += 15
    elif roe and roe > 10:
        s += 5
    if pe and pe < 20:
        s += 10
    elif pe and pe > 40:
        s -= 15
    if debt and debt > 70:
        s -= 15
    return max(0.0, min(100.0, s))
