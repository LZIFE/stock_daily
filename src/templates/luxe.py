#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑲ 奢华黑金：近黑底、香槟金细线、衬线大字、极致留白"""
from . import common as C

BG, GOLD, CHAMP, INK, MUT = "#0b0a08", "#c9a962", "#e8d9b0", "#f4efe4", "#8d8574"
SERIF = "Georgia,Songti SC,STSong,serif"


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers = ctx["indices"], ctx["tiers"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))
    tb, dg = tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": CHAMP, "muted": MUT},
                         "The maison's AI atelier awaits AGNES_API_KEY.")
    SANS_L = "'Helvetica Neue',Arial,'PingFang SC',sans-serif"

    idx_line = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(
        f"<span style='color:{MUT}'>{C.esc(d['name'])}</span> "
        f"<span style='color:{'#d4b57a' if d['chg_today']>0 else '#7fa08c'}'>{d['chg_today']:+.2f}%</span>"
        for d in idx)

    pieces = "".join(
        f"""<tr><td style="padding:22px 0 20px;border-bottom:1px solid #2a251c">
<table width="100%" cellpadding="0" cellspacing="0"><tr>
<td width="70" valign="top"><span style="font-family:{SERIF};font-size:13px;color:{GOLD};letter-spacing:2px">№ {i + 1:02d}</span></td>
<td>
<div style="font-family:{SERIF};font-size:24px;letter-spacing:4px;color:{INK}">{C.esc(r['name'])}
<span style="font-size:12px;color:{MUT};letter-spacing:1px">&nbsp;&nbsp;{r['code']}</span></div>
<div style="font-family:{SANS_L};font-size:11px;letter-spacing:3px;color:{GOLD};margin:6px 0 8px;text-transform:uppercase">
PE {r['pe_now']:.1f}&nbsp;&nbsp;·&nbsp;&nbsp;NP +{r['np_yoy']:.0f}%&nbsp;&nbsp;·&nbsp;&nbsp;SCORE {r['score']}</div>
<div style="font-family:{SANS_L};font-size:12.5px;line-height:2;color:#bdb5a3">{C.esc(r.get('_reason') or '')}</div>
</td>
<td align="right" valign="top"><span style="font-family:{SERIF};font-size:15px;color:{CHAMP}">{r['close']:.2f}</span></td>
</tr></table></td></tr>"""
        for i, r in enumerate(ta))

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:30px 10px;font-family:{SANS_L}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

<tr><td style="text-align:center;padding:18px 0 8px">
  <div style="font-size:10.5px;letter-spacing:8px;color:{GOLD}">MAISON&nbsp;DE&nbsp;LA&nbsp;BOURSE</div>
  <div style="font-family:{SERIF};font-size:34px;color:{INK};letter-spacing:12px;margin:14px 0 10px">甄 选 日 报</div>
  <div style="width:60px;height:1px;background:{GOLD};margin:0 auto"></div>
  <div style="font-size:10.5px;letter-spacing:4px;color:{MUT};margin-top:12px">CURATED · DAILY · {ctx['data_date']}</div>
</td></tr>

<tr><td style="text-align:center;padding:16px 0 4px;font-size:11.5px;color:#a89f8d;letter-spacing:1px">{idx_line}</td></tr>

<tr><td style="padding:26px 0 0">
  <div style="text-align:center;font-family:{SERIF};color:{GOLD};font-size:13px;letter-spacing:5px;margin-bottom:4px">— 今日臻选 —</div>
  {''.join(pieces) or '<p style="text-align:center;color:%s;font-family:%s">今日暂无入选之作</p>' % (MUT, SERIF)}
</td></tr>

<tr><td style="padding:26px 0 0">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="50%" valign="top" style="padding-right:14px">
      <div style="border:1px solid #2a251c;padding:14px 16px">
       <div style="font-family:{SERIF};font-size:13px;color:{GOLD};letter-spacing:3px;margin-bottom:8px">候 班（{len(tb)}）</div>
       <div style="font-size:11.5px;line-height:2.1;color:#9a917f">{"、".join(C.esc(r['name']) for r in tb[:10]) or "—"}</div></div>
    </td>
    <td valign="top" style="padding-left:14px">
      <div style="border:1px solid #2a251c;padding:14px 16px">
       <div style="font-family:{SERIF};font-size:13px;color:{GOLD};letter-spacing:3px;margin-bottom:8px">敬 而 远 之（{len(dg)}）</div>
       <div style="font-size:11.5px;line-height:2.1;color:#9a917f">{(C.esc(dg[0]['name']) if dg else "—")}</div></div>
    </td>
  </tr></table>
</td></tr>

<tr><td style="padding:28px 0 0">
  <div style="border-top:1px solid #2a251c;border-bottom:1px solid #2a251c;padding:16px 18px;text-align:center">
   <div style="font-size:10px;letter-spacing:5px;color:{GOLD};margin-bottom:7px">LE MOT D'AGNES</div>
   <div style="font-size:12.5px;line-height:2;color:#cfc7b5;text-align:left">{ai_body}</div>
  </div>
</td></tr>

<tr><td style="padding:20px 24px 10px;text-align:center;color:#57503f;font-size:9.5px;line-height:1.9;
      letter-spacing:0.5px">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
