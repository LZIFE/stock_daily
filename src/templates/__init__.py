#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模板注册表（20款）"""
from . import (arcade, brew, changelog, classic, dashboard, editorial, focus,
               imperial, infographic, journal, letter, luxe, neon, newspaper,
               pastel, readme_tpl, swiss, terminal, vogue, zen)

REGISTRY = {
    "classic": classic.render,
    "terminal": terminal.render,
    "editorial": editorial.render,
    "newspaper": newspaper.render,
    "imperial": imperial.render,
    "pastel": pastel.render,
    "swiss": swiss.render,
    "focus": focus.render,
    "letter": letter.render,
    "dashboard": dashboard.render,
    "changelog": changelog.render,
    "brew": brew.render,
    "readme": readme_tpl.render,
    "vogue": vogue.render,
    "journal": journal.render,
    "zen": zen.render,
    "neon": neon.render,
    "arcade": arcade.render,
    "luxe": luxe.render,
    "infographic": infographic.render,
}

LABELS = {
    "classic": "① 经典深蓝金融",
    "terminal": "② 终端暗黑风",
    "editorial": "③ 极简杂志风",
    "newspaper": "④ 报纸风（财经老报）",
    "imperial": "⑤ 红金研报风",
    "pastel": "⑥ 清新卡片风",
    "swiss": "⑦ 瑞士网格风",
    "focus": "⑧ 今日聚焦 · Top3深读",
    "letter": "⑨ 订阅信件 · 书信叙事",
    "dashboard": "⑩ 数据驾驶舱",
    "changelog": "⑪ 更新日志 · Changelog",
    "brew": "⑫ 晨报简报 · Brew风",
    "readme": "⑬ 工程文档 · README风",
    "vogue": "⑭ 时尚大片 · THE POOL",
    "journal": "⑮ 手账涂鸦",
    "zen": "⑯ 日式侘寂",
    "neon": "⑰ 赛博朋克霓虹",
    "arcade": "⑱ 像素街机",
    "luxe": "⑲ 奢华黑金",
    "infographic": "⑳ 信息图数据新闻",
}


def render(name, ctx):
    return REGISTRY.get(name, classic.render)(ctx)
