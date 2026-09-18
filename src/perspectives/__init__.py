#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""perspective 评分函数注册表。
每个函数输入 r (单只股票 dict) 和 ctx (市场上下文)，输出 0-100 分。

分组说明见 config/score_weights.json (v1) 与 config/score_weights_v2.json (v2)。
v2 核心分只用 4 本「有独立增量信息」的书：coulling / candlestick / buffett / shefrin。
"""
from . import wyckoff, edwards_magee, head_first, chanlun
from . import damodaran, graham, tangchao, fisher
from . import howard_marks, livermore, kahneman, munger
from . import coulling, dow, candlestick, malkiel
from . import buffett, shefrin

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
    # 兼容/制衡
    "dow": dow.score,
    "malkiel": malkiel.score,
    # v2 核心分（依据作者级边际贡献证据，见 SCORING_V2.md）
    "coulling": coulling.score,
    "candlestick": candlestick.score,
    "buffett": buffett.score,
    "shefrin": shefrin.score,
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
    "dow": "道氏理论",
    "malkiel": "马尔基尔·随机漫步(制衡)",
    "coulling": "邱国鹭·便宜且不拥挤",
    "candlestick": "蜡烛图·K线形态",
    "buffett": "巴菲特·现金利润质量",
    "shefrin": "舍夫林·低波动偏好",
}

# v2 共识分只用「真实实现」的模块；恒返回常数的模块计入会向中位稀释
# （malkiel 恒返回 50，制衡逻辑由 score_engine 处理）
CONSENSUS_MODULES = [m for m in REGISTRY if m != "malkiel"]


def score_all(r, ctx):
    """对单只股票调用所有已注册 perspective，返回 {name: score}"""
    out = {}
    for name, fn in REGISTRY.items():
        try:
            s = fn(r, ctx)
        except Exception:
            s = None
        if s is None:
            s = 50.0
        out[name] = max(0.0, min(100.0, float(s)))
    return out
