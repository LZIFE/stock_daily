#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑰ 赛博朋克霓虹：深紫夜幕、霓虹描边、玻璃拟态卡片"""
from . import common as C

BG, LINE = "#0d0221", "#2a1458"
PINK, CYAN, LIME, VIOLET = "#ff2df7", "#00f0ff", "#adff2f", "#9d4edd"
TXT, MUT = "#e6e0ff", "#7a6fa8"

T = {"fs": "12.5px", "cell_pad": "6px 5px", "th_fs": "11px",
     "name_c": CYAN, "text_c": TXT, "muted": MUT,
     "th_c": PINK, "row_border": f"1px solid {LINE}",
     "up": PINK, "down": LIME, "flat": MUT,
     "bar_track": LINE, "reason_c": "#a89fd0",
     "badge_bg": "#1b0838", "badge_fg": LIME}


def _glass(inner, border=CYAN, bg="#150533"):
    return (f"<div style='background:{bg};border:1px solid {border};border-radius:14px;"
            f"box-shadow:0 0 18px {border}44;padding:13px 15px;margin:10px 0'>{inner}</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": TXT, "muted": MUT},
                         "// NEURAL LINK OFFLINE — insert AGNES_API_KEY to boot.")

    idx_cards = "<table width='100%' cellpadding='0' cellspacing='0'><tr>" + "".join(
        f"<td style='padding:4px'><div style='background:#1b0838;border:1px solid {VIOLET};"
        f"border-radius:10px;padding:10px 4px;text-align:center'>"
        f"<div style='font-size:11px;color:{MUT}'>{C.esc(d['name'])}</div>"
        f"<div style='font-size:16px;font-weight:800;color:{TXT};margin-top:2px'>{C.num(d['close'])}</div>"
        f"<div style='font-size:12px;font-weight:700;color:{PINK if d['chg_today']>0 else LIME}'>{d['chg_today']:+.2f}%</div>"
        f"</div></td>" for d in idx) + "</tr></table>"

    def sec(title, color, rows):
        head = (f"<div style='color:{color};font-size:13.5px;font-weight:800;letter-spacing:1px;margin-bottom:6px'>"
                f"◤ {title} <span style='float:right;color:{MUT}'>[{len(rows)}]</span></div>")
        return _glass(head + C.stock_table(rows, T), color)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:22px 8px;font-family:-apple-system,'PingFang SC',sans-serif;
     background-image:repeating-linear-gradient(0deg,#ffffff06 0 1px,transparent 1px 42px)">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%">

<tr><td style="text-align:center;padding:14px 0 4px">
  <div style="font-size:30px;font-weight:900;letter-spacing:3px;color:{CYAN};
       text-shadow:0 0 14px {CYAN}88">NEON<span style="color:{PINK};text-shadow:0 0 14px {PINK}88">//</span>POOL</div>
  <div style="font-size:11px;letter-spacing:4px;color:{MUT};margin-top:4px">
   加仓池日报 · NIGHT SHIFT · {ctx['data_date']}</div>
</td></tr>

<tr><td>{_glass(idx_cards, VIOLET)}</td></tr>

<tr><td>
  {_glass(f"<span style='color:{LIME};font-weight:700;font-size:13px'>▲ SIGNAL STRENGTH</span>"
          f"&nbsp;&nbsp;<span style='font-size:12px;color:{MUT}'>池内 {st['up']}↑ / {st['down']}↓ · "
          f"平均 {st['avg']:+.2f}% · 第一档均PE {st['ta_avg_pe'] or '—'}</span>", LIME)}
  {sec('第一档 · 强势回踩', CYAN, ta)}
  {sec('第二档 · 深度回踩', PINK, tb)}
  {sec('追高风险 · OVERHEAT', '#ff5555', dg)}
</td></tr>

<tr><td>{_glass(
    f"<div style='color:{PINK};font-weight:800;font-size:13px;margin-bottom:5px'>⌁ AGNES NEURAL COMMENTARY</div>"
    f"<div style='font-size:13px;line-height:1.9;color:{TXT}'>{ai_body}</div>", PINK)}</td></tr>

<tr><td style="padding:12px 6px 18px;color:#5c5382;font-size:10.5px;line-height:1.8">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
