#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14 个 perspective 评分函数注册表。
每个函数输入 r (单只股票 dict) 和 ctx (市场上下文)，输出 0-100 分。
"""
from . import wyckoff, edwards_magee, head_first, chanlun
from . import damodaran, graham, tangchao, fisher
from . import howard_marks, livermore, kahneman, munger
from . import coulling, dow, candlestick, malkiel

REGISTRY = {
    # 量价组
    "wyckoff": wyckoff.score,
    "edwards_magee": edwards_magee.score,
    "head_first": head_first.score,
    "chanlun": chanlun.score,
    # 价值组
    "damodaran": damodaran.score,
    "graham": graham.score,
    "tangchao": tangchao.score,
    "fisher": fisher.score,
    # 心理纪律组
    "howard_marks": howard_marks.score,
    "livermore": livermore.score,
    "kahneman": kahneman.score,
    "munger": munger.score,
    # 兼容/制衡 (暂未计入主权重, 但保留)
    "coulling": coulling.score,
    "dow": dow.score,
    "candlestick": candlestick.score,
    "malkiel": malkiel.score,
}

LABELS = {
    "wyckoff": "威科夫·量价资金",
    "edwards_magee": "爱德华兹-麦吉·趋势形态",
    "head_first": "正帆·三阶段+产业",
    "chanlun": "缠论·中枢背驰",
    "damodaran": "达摩达兰·估值三要素",
    "graham": "格雷厄姆·安全边际",
    "tangchao": "唐朝·财报排雷",
    "fisher": "费雪·成长股",
    "howard_marks": "霍华德马克斯·周期温度",
    "livermore": "利弗莫尔·趋势金字塔",
    "kahneman": "卡尼曼·冲动抑制",
    "munger": "芒格·避开愚蠢",
}


def score_all(r, ctx):
    """对单只股票调用所有已注册 perspective，返回 {name: score}"""
    out = {}
    for name, fn in REGISTRY.items():
        try:
            s = fn(r, ctx)
        except Exception:
            s = 50.0
        if s is None:
            s = 50.0
        out[name] = max(0.0, min(100.0, float(s)))
    return out
