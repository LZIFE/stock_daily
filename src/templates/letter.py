#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑨ 订阅信件：无表格，全叙事书信体，数据织进文字里"""
from . import common as C

PAPER, INK, MUTED = "#faf6ef", "#2b2118", "#8c7f6d"


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench, st = ctx["indices"], ctx["tiers"], ctx["bench"], ctx["stats"]
    date_cn = ctx["data_date"].replace("-", " 年 ").replace(" 年 ", "年", 1) + ""
    y, m, d = ctx["data_date"].split("-")
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))
    tb = tiers.get("tier_b", [])
    dg = tiers.get("danger", [])

    def nm(r):
        return f"<b style='color:#7a5c1e'>{C.esc(r['name'])}</b>"

    ta_para = "。".join(
        f"{nm(r)}（{r['code']}）值得多看一眼——{C.esc(r.get('_reason') or '')}"
        for r in ta[:4]) + ("。" if ta else "")
    idx_para = "；".join(f"{C.esc(d['name'])}{d['chg_today']:+.2f}%" for d in idx)
    tb_para = (f"{nm(tb[0])}、{nm(tb[1])}" if len(tb) >= 2 else (nm(tb[0]) if tb else "暂无")) \
        if tb else "暂无"
    dg_para = "、".join(nm(r) for r in dg) or "无"

    ai_body = C.ai_block(ctx["ai_text"], {"ai_fs": "13px", "ai_c": "#4a4033", "muted": MUTED},
                         "（AI 笔友尚未上线——配置 AGNES_API_KEY 后，这里会有一段更个人化的市场信札。）")

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{MUTED}">
<div style="padding:26px 10px;font-family:Georgia,'Songti SC','STSong',serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{PAPER};
       border-radius:4px;box-shadow:0 8px 30px #00000030">

<tr><td style="padding:34px 44px 0;text-align:center">
  <div style="font-size:11px;letter-spacing:5px;color:{MUTED}">A LETTER FROM THE MARKET</div>
  <div style="border-bottom:1px solid #d9cdb8;padding:10px 0 14px;margin-top:8px">
    <span style="font-size:20px;color:{INK};letter-spacing:8px">市 场 书 简</span></div>
</td></tr>

<tr><td style="padding:24px 44px 10px;font-size:14.5px;line-height:2.1;color:#3d3327">
  <p style="margin:0 0 14px">见字如面。</p>
  <p style="margin:0 0 14px">{y}年{m}月{d}日，收盘了。今天的盘面并不平静——{idx_para}。
  池内 {st['n']} 只标的中，{st['up']} 只上涨、{st['down']} 只下跌，
  平均 {st['avg']:+.2f}%。基准 {C.esc(bench['name'])} 收在 {bench['close']:,.2f}。</p>
  <p style="margin:0 0 14px">按老规矩筛了一遍，第一档浮出 {len(ta)} 张面孔。{ta_para}</p>
  <p style="margin:0 0 14px">第二档里，{tb_para} 还在深水区扑腾——它们不缺故事，缺的是一根放量止跌的阳线。
  而追高风险名单上的 {dg_para}，就让它飞一会儿吧，我们不去接。</p>
  <p style="margin:0">仓位的事，老生常谈：分批、留子弹、别和趋势赌气。市场每天都在，机会不差这一天。</p>
</td></tr>

<tr><td style="padding:6px 44px 18px">
  <div style="border-left:3px solid #b08d3e;background:#f3ecdd;padding:12px 16px;border-radius:0 6px 6px 0;
        font-size:13px;line-height:1.9;color:#4a4033">
    <span style="letter-spacing:3px;color:#7a5c1e;font-size:11px">附言 · AI 点评 BY AGNES</span><br>{ai_body}
  </div>
</td></tr>

<tr><td style="padding:0 44px 30px;text-align:right">
  <div style="color:{INK};font-size:14px">你的市场观察员</div>
  <div style="color:{MUTED};font-size:12px;margin-top:2px">{y}.{m}.{d}　夜</div>
</td></tr>

<tr><td style="padding:12px 44px;border-top:1px solid #d9cdb8">
  <div style="color:#b0a48e;font-size:10.5px;line-height:1.7">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
