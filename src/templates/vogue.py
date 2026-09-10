#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑭ 时尚大片：THE POOL —— 高级编辑感排版

设计基调：纸白底、墨黑衬线大字、发丝线分隔、一点绛红。
邮件客户端兼容要点（不要改坏）：
- HTML 属性一律用双引号；字体栈内不得出现引号（否则 style 属性被截断）。
- 不用 linear-gradient / td margin / float 等邮件客户端不可靠的样式。
"""
from . import common as C

INK, PAPER, MUT = "#141414", "#faf9f6", "#8a857a"
RED, UP, DOWN = "#b3122e", "#b3122e", "#1e6b45"
HAIR = "#e3e0d8"
SERIF = "Didot,Bodoni MT,Songti SC,STSong,Georgia,serif"
SANS = "Helvetica,Arial,PingFang SC,Microsoft YaHei,sans-serif"
BAND = {"tier_a": "#1e6b45", "tier_b": "#2f5a8f", "watch": "#a06a1b",
        "danger": "#8f1d1d", "frozen": "#6b7280", "excluded": "#6b7280"}
BAND_LABEL = {"tier_a": "A 档", "tier_b": "B 档", "watch": "观察", "danger": "追高",
              "frozen": "冻结", "excluded": "排除"}


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))
    tb, dg = tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#e9e5da", "muted": "#8f897c"},
                         "The AI edit is not in this issue yet — AGNES_API_KEY required.")

    # ---------- 指数条 ----------
    n = len(idx) or 1
    idx_cells = ""
    for i, d in enumerate(idx):
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else MUT)
        border = "" if i == 0 else f"border-left:1px solid {HAIR};"
        idx_cells += (f'<td width="{100 // n}%" align="center" style="padding:14px 2px;{border}">'
                      f'<div style="font-family:{SANS};font-size:10.5px;letter-spacing:2px;color:{MUT}">'
                      f'{C.esc(d["name"])}</div>'
                      f'<div style="font-family:{SERIF};font-size:19px;color:{INK};margin:4px 0">'
                      f'{d["close"]:,.2f}</div>'
                      f'<div style="font-family:{SANS};font-size:11.5px;font-weight:600;color:{c}">'
                      f'{d["chg_today"]:+.2f}%</div></td>')

    # ---------- 个股阵容 ----------
    rows = []
    for i, r in enumerate(ta):
        name, code = C.esc(r["name"]), r["code"]
        reason = C.esc(r.get("_reason") or "")
        chg = r["chg_today"]
        chg_c = UP if chg > 0 else (DOWN if chg < 0 else MUT)
        zone = "NEAR MA20" if abs(r.get("vs_ma20") or 9) <= 2 else "PULLBACK"
        metrics = "PE {0:.1f} · NP +{1:.0f}% · {2}".format(r["pe_now"], r["np_yoy"], zone)

        multi = ""
        if r.get("_multi_total") is not None:
            band = r["_multi_band"]
            bcolor = BAND.get(band, "#6b7280")
            blabel = BAND_LABEL.get(band, band)
            cap = r.get("_position_cap", 0)
            multi = (f'<div style="margin-top:8px;padding-top:7px;border-top:1px dotted {HAIR};'
                     f'font-family:{SANS};font-size:11px;color:{MUT};letter-spacing:1px">'
                     f'多视角 <b style="font-family:{SERIF};font-size:16px;color:{INK};'
                     f'letter-spacing:0">{r["_multi_total"]:.0f}</b>'
                     f'&nbsp;·&nbsp;<span style="color:{bcolor};font-weight:700">{blabel}</span>'
                     f'&nbsp;·&nbsp;建议仓位≤{cap:.0f}%</div>')
            if r.get("_multi_veto"):
                multi += (f'<div style="font-family:{SANS};font-size:10.5px;color:#8f1d1d;'
                          f'margin-top:3px">⚠ {C.esc(r["_multi_veto"][0])}</div>')

        rows.append(f'<tr><td style="padding:16px 0;border-bottom:1px solid {HAIR}">'
                    f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
                    f'<td width="52" valign="top"><span style="font-family:{SERIF};font-size:25px;'
                    f'color:#cdc8bb;font-weight:700">{i + 1:02d}</span></td>'
                    f'<td valign="top">'
                    f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
                    f'<td><span style="font-family:{SERIF};font-size:20px;color:{INK}">{name}</span>'
                    f'<span style="font-family:{SANS};font-size:11px;color:{MUT};'
                    f'letter-spacing:1px;margin-left:6px">{code}</span></td>'
                    f'<td align="right"><span style="font-family:{SANS};font-size:14px;'
                    f'font-weight:700;color:{chg_c}">{chg:+.2f}%</span></td>'
                    f'</tr></table>'
                    f'<div style="font-family:{SANS};font-size:11px;letter-spacing:1.5px;'
                    f'color:{MUT};margin-top:4px">{metrics}</div>'
                    f'<div style="font-family:{SANS};font-size:12.5px;line-height:1.7;'
                    f'color:#45423c;margin-top:5px">{reason}</div>'
                    f'{multi}'
                    f'</td></tr></table></td></tr>')
    empty_row = ('<tr><td style="padding:24px 0;text-align:center;font-family:'
                 + SANS + ';font-size:13px;color:' + MUT + '">本期无入选阵容</td></tr>')
    lineup = "".join(rows) or empty_row

    tb_names = "、".join(C.esc(r["name"]) for r in tb[:12]) or "—"
    dg_names = "、".join(C.esc(r["name"]) for r in dg[:8]) or "—"

    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{PAPER}">
<div style="padding:30px 10px;font-family:{SANS}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%">

<tr><td style="padding:0 0 10px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="font-family:{SANS};font-size:10px;letter-spacing:3px;color:{MUT}">
      VOL.{ctx["data_date"].replace("-", ".")}</td>
    <td align="right" style="font-family:{SANS};font-size:10px;letter-spacing:3px;color:{MUT}">
      DAILY EDITION · 多书视角特辑</td>
  </tr></table>
</td></tr>

<tr><td style="border-top:1px solid {INK};border-bottom:3px double {INK};text-align:center;padding:18px 0 16px">
  <div style="font-family:{SERIF};font-size:46px;font-weight:700;letter-spacing:12px;color:{INK}">THE&nbsp;POOL</div>
  <div style="font-family:{SERIF};font-size:14px;letter-spacing:2px;color:{MUT};margin-top:8px">
    本季，<span style="color:{RED}">回踩</span>是最好的入场券。</div>
</td></tr>

<tr><td style="border-left:1px solid {HAIR};border-right:1px solid {HAIR};border-bottom:1px solid {HAIR}">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>{idx_cells}</tr></table>
</td></tr>

<tr><td style="padding:26px 0 6px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="font-family:{SERIF};font-size:16px;letter-spacing:3px;color:{INK}">今日阵容</td>
    <td align="right" style="font-family:{SANS};font-size:10.5px;letter-spacing:2px;color:{MUT}">
      {len(ta)} SELECTED · {st["up"]} UP / {st["down"]} DOWN · AVG {st["avg"]:+.2f}%</td>
  </tr></table>
</td></tr>

<tr><td style="border-top:1px solid {INK};padding:4px 0 0">
  <table width="100%" cellpadding="0" cellspacing="0">{lineup}</table>
</td></tr>

<tr><td style="padding:26px 0 8px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="50%" valign="top" style="padding-right:14px;border-right:1px solid {HAIR}">
      <div style="font-family:{SERIF};font-size:14px;letter-spacing:3px;color:{INK};padding-bottom:6px">候场中 · {len(tb)}</div>
      <div style="font-family:{SANS};font-size:12px;line-height:2;color:#55524a">{tb_names}</div>
    </td>
    <td width="50%" valign="top" style="padding-left:14px">
      <div style="font-family:{SERIF};font-size:14px;letter-spacing:3px;color:{INK};padding-bottom:6px">谢幕名单 · {len(dg)}</div>
      <div style="font-family:{SANS};font-size:12px;line-height:2;color:#55524a">{dg_names}</div>
    </td>
  </tr></table>
</td></tr>

<tr><td style="padding:14px 0"></td></tr>

<tr><td style="background:{INK};padding:20px 24px">
  <div style="font-family:{SANS};font-size:10px;letter-spacing:3px;color:#a39d8f;padding-bottom:8px">
    THE AI EDIT — BY AGNES</div>
  <div style="font-family:{SANS};color:#e9e5da;font-size:13px;line-height:1.9">{ai_body}</div>
</td></tr>

<tr><td style="padding:16px 0 2px;border-top:1px solid {HAIR};text-align:center;
      color:#a8a49a;font-family:{SANS};font-size:10px;line-height:1.8;letter-spacing:1px">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>'''
