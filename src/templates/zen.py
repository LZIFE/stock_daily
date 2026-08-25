#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑯ 日式侘寂：极致留白、细灰、纵向节奏，一枚朱印点缀"""
from . import common as C

BG, INK, GRAY, HAIR, VERMILION = "#fafaf8", "#2b2b2b", "#9b9b94", "#e8e8e4", "#b3402a"


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_fs": "13px", "ai_c": "#4a4a44", "muted": GRAY},
                         "（静默。AGNES_API_KEY 配置后，此处有言。）")

    def row(r, i):
        return (f"<tr><td style='padding:13px 0;border-bottom:1px solid {HAIR}'>"
                f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
                f"<td style='font-size:15px;color:{INK};letter-spacing:1px'>{C.esc(r['name'])}"
                f"&nbsp;<span style='font-size:11px;color:{GRAY}'>{r['code']}</span></td>"
                f"<td align='right'><span style='font-size:12px;color:{GRAY}'>现价 {r['close']:.2f}</span>"
                f"&nbsp;&nbsp;<span style='font-size:13px;color:{VERMILION if r['chg_today']>0 else '#4f7d68'}'"
                f">{r['chg_today']:+.2f}%</span></td></tr></table>"
                f"<div style='font-size:12px;line-height:1.9;color:#6d6d66;margin-top:5px'>{C.esc(r.get('_reason') or '')}</div>"
                f"</td></tr>")

    idx_rows = "".join(
        f"<tr><td style='padding:7px 0;font-size:12.5px;color:{GRAY};border-bottom:1px solid {HAIR}'>"
        f"{C.esc(d['name'])}<span style='float:right;color:{INK}'>{d['close']:,.2f}"
        f"&nbsp;<span style='color:{VERMILION if d['chg_today']>0 else '#4f7d68'}'>{d['chg_today']:+.2f}%</span></span></td></tr>"
        for d in idx)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:40px 10px;font-family:-apple-system,'PingFang SC','Hiragino Sans',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%">

<tr><td style="text-align:center;padding:14px 0 30px">
  <div style="display:inline-block;width:34px;height:34px;background:{VERMILION};color:#fff;
        font-size:15px;line-height:34px;border-radius:3px">池</div>
  <div style="font-size:11px;letter-spacing:6px;color:{GRAY};margin-top:12px">毎 日 一 覧</div>
</td></tr>

<tr><td style="border-top:1px solid {INK};padding-top:18px">
  <table width="100%" cellpadding="0" cellspacing="0">{idx_rows}</table>
  <p style="font-size:12.5px;line-height:2.2;color:#55554e;margin:20px 0">
   今日池内、{st['up']} 上/{st['down']} 下。平均 {st['avg']:+.2f}%。
   第一档 {ctx['counts']['tier_a']}、第二档 {ctx['counts']['tier_b']}、
   高位 {ctx['counts']['danger']}、观望 {ctx['counts']['watch']}。
   数据日　{ctx['data_date']}。</p>
</td></tr>

<tr><td style="padding:16px 0 0">
  <div style="font-size:12px;letter-spacing:4px;color:{GRAY};margin-bottom:4px">一　候 补</div>
  <table width="100%" cellpadding="0" cellspacing="0">{''.join(row(r, i) for i, r in enumerate(ta)) or ''}</table>
</td></tr>

<tr><td style="padding:28px 0 0">
  <div style="font-size:12px;letter-spacing:4px;color:{GRAY};margin-bottom:10px">二　待 機（{len(tb)}）</div>
  <p style="font-size:12.5px;line-height:2.2;color:#6d6d66;margin:0">
   {"、".join(C.esc(r['name']) for r in tb[:12]) or "なし"}——
   信号を待つ。</p>
</td></tr>

<tr><td style="padding:24px 0 0">
  <div style="font-size:12px;letter-spacing:4px;color:{GRAY};margin-bottom:10px">三　遠 慮（{len(dg)}）</div>
  <p style="font-size:12.5px;line-height:2.2;color:#6d6d66;margin:0">
   {(C.esc(dg[0]['name']) if dg else "無し")}{" ほか" if len(dg) > 1 else ""}——
   高所につき、見送り。</p>
</td></tr>

<tr><td style="padding:34px 0 0;border-top:1px solid {HAIR}">
  <div style="font-size:12px;letter-spacing:4px;color:{GRAY};margin-bottom:8px">四　AI の 言（Agnes）</div>
  <div style="font-size:13px;line-height:2.2;color:#4a4a44">{ai_body}</div>
</td></tr>

<tr><td style="padding:36px 0 8px;text-align:right">
  <span style="display:inline-block;border:1.5px solid {VERMILION};color:{VERMILION};
       font-size:11px;padding:4px 8px;letter-spacing:3px;margin-right:8px">投資注意</span>
</td></tr>
<tr><td style="padding:0 0 20px;color:#c2c2bc;font-size:10px;line-height:1.9">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
