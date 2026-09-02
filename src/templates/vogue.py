#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑭ 时尚大片：Vogue杂志风，超大衬线标题、黑白灰+一点红、编辑感排版"""
from . import common as C

INK, PAPER, MUT, RED = "#0a0a0a", "#f5f4f0", "#9a968c", "#c1121f"
SERIF = "'Didot','Bodoni MT','Songti SC','STSong',serif"
SANS = "Helvetica,Arial,'PingFang SC',sans-serif"


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))
    tb, dg = tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": INK, "muted": MUT},
                         "The AI edit is not in this issue yet — AGNES_API_KEY required.")

    lineup = "".join(
        f"<tr><td style='padding:14px 0;border-bottom:1px solid #d8d5cd'>"
        f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
        f"<td width='64' valign='top'><span style='font-family:{SERIF};font-size:30px;color:#cfcbc0;"
        f"font-weight:700'>{i + 1:02d}</span></td>"
        f"<td valign='top'>"
        f"<div style='font-family:{SERIF};font-size:21px;letter-spacing:2px;color:{INK}'>{C.esc(r['name'])}"
        f"&nbsp;<span style='font-size:11px;color:{MUT};letter-spacing:1px'>{r['code']}</span></div>"
        f"<div style='font-family:{SANS};font-size:11px;letter-spacing:2px;text-transform:uppercase;"
        f"color:{MUT};margin:3px 0 5px'>PE {r['pe_now']:.1f} · NP +{r['np_yoy']:.0f}% · "
        f"{'NEAR MA20' if abs(r.get('vs_ma20') or 9) <= 2 else 'PULLBACK'} </div>"
        f"<div style='font-family:{SANS};font-size:12.5px;line-height:1.7;color:#40403a'>{C.esc(r.get('_reason') or '')}</div>"
        # 多视角评分行: 总分 + 档位徽章 + 仓位上限 + 否决原因
        + (
            f"<div style='font-family:{SANS};font-size:11px;margin-top:6px;line-height:1.6'>"
            f"<span style='color:{MUT};letter-spacing:1.5px;text-transform:uppercase'>多视角</span> "
            f"<b style='font-family:{SERIF};font-size:18px;color:{INK}'>{r['_multi_total']:.0f}</b>"
            f"&nbsp;<span style='background:{('#059669' if r['_multi_band']=='tier_a' else ('#2563eb' if r['_multi_band']=='tier_b' else ('#dc2626' if r['_multi_band'] in ('danger','excluded') else '#d97706')))};"
            f"color:#fff;border-radius:99px;padding:1px 7px;font-size:10px;font-weight:600;letter-spacing:1px'>"
            f"{ {'tier_a':'A','tier_b':'B','watch':'观察','danger':'追高','frozen':'冻结','excluded':'排除'}.get(r['_multi_band'], r['_multi_band']) }</span>"
            f"&nbsp;<span style='color:{MUT}'>仓位≤{r.get('_position_cap',0):.0f}%</span>"
            + (f"<div style='color:#8f1d1d;font-size:10.5px;margin-top:2px'>⚠ {C.esc(r['_multi_veto'][0])}</div>" if r.get('_multi_veto') else "")
            + "</div>"
          ) if r.get("_multi_total") is not None else ""
        +
        f"</td>"
        f"<td align='right' valign='top'><span style='font-family:{SANS};font-size:13px;font-weight:700;color:"
        f"{'#8f1d1d' if r['chg_today'] > 0 else '#1a5632'}'>{r['chg_today']:+.2f}%</span></td>"
        f"</tr></table></td></tr>"
        for i, r in enumerate(ta))

    idx_line = "&nbsp;&nbsp;&nbsp;&nbsp;".join(
        f"<span style='color:{MUT}'>{C.esc(d['name'])}</span> "
        f"<b style='color:{'#8f1d1d' if d['chg_today']>0 else '#1a5632'}'>{d['close']:,.2f} ({d['chg_today']:+.2f}%)</b>"
        for d in idx)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{PAPER}">
<div style="padding:26px 10px;font-family:{SANS}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%">

<tr><td style="text-align:center;padding:10px 0 4px">
  <div style="font-family:{SERIF};font-size:52px;font-weight:700;letter-spacing:14px;color:{INK}">THE&nbsp;POOL</div>
  <div style="border-top:1px solid {INK};border-bottom:1px solid {INK};padding:5px 0;margin-top:6px">
    <span style="font-size:10.5px;letter-spacing:4px;color:{MUT}">VOL.{ctx['data_date'].replace('-', '.')}
    &nbsp;·&nbsp; DAILY EDITION &nbsp;·&nbsp; 多书视角特辑</span>
  </div>
</td></tr>

<tr><td style="text-align:center;padding:16px 0 6px">
  <div style="font-family:{SERIF};font-size:27px;line-height:1.35;color:{INK}">
    本季，<span style="color:{RED}">回踩</span>是最好的入场券。</div>
  <div style="font-size:11px;letter-spacing:2px;color:{MUT};margin-top:8px">{idx_line}</div>
</td></tr>

<tr><td style="background:linear-gradient(120deg,#e7e4dc,#cfccc2 60%,#e7e4dc);height:110px;border-radius:2px;
      margin:10px 0;display:block;text-align:center;vertical-align:middle">
  <div style="padding-top:34px;font-family:{SERIF};color:#55524a;letter-spacing:6px;font-size:15px">— 今日阵容 —</div>
  <div style="font-family:{SANS};font-size:11px;color:{MUT};letter-spacing:2px;padding-top:4px">
   {len(ta)} SELECTED · {st['up']} UP / {st['down']} DOWN · AVG {st['avg']:+.2f}%</div>
</td></tr>

<tr><td style="padding:6px 0 0">
  <table width="100%" cellpadding="0" cellspacing="0">{lineup or "<tr><td><i>本期无入选阵容</i></td></tr>"}</table>
</td></tr>

<tr><td style="padding:18px 0 4px">
  <div style="font-family:{SERIF};font-size:15px;letter-spacing:3px;color:{INK};margin-bottom:6px">BACKSTAGE · 后台名单</div>
  <p style="font-size:12.5px;line-height:2;color:#55524a;margin:0">
   <span style='color:{MUT}'>候场中（{len(tb)}）：</span>{"、".join(C.esc(r['name']) for r in tb[:12]) or "—"}　
   <span style='color:{MUT}'>｜本季谢幕，请勿追光（{len(dg)}）：</span>{(C.esc(dg[0]['name']) if dg else "—")} 等</p>
</td></tr>

<tr><td style="background:{INK};padding:16px 20px;margin:12px 0">
  <div style="color:#d9d6cd;font-size:11px;letter-spacing:3px;margin-bottom:6px">THE AI EDIT — BY AGNES</div>
  <div style="color:#efece4;font-size:13px;line-height:1.9">{ai_body}</div>
</td></tr>

<tr><td style="text-align:center;padding:14px 30px;color:#a8a49a;font-size:10px;line-height:1.8;
      letter-spacing:1px">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
