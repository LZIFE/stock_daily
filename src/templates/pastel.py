#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑥ 清新卡片风：浅底大圆角、柔和色块、宽松呼吸感"""
from . import common as C

BG, CARD, BORDER, INK, MUTED = "#eef1fa", "#ffffff", "#e6e9f5", "#1e293b", "#94a3b8"
UP, DOWN = "#ef4444", "#10b981"

T = {"fs": "13.5px", "cell_pad": "9px 6px", "th_fs": "12px",
     "name_c": INK, "text_c": "#475569", "muted": MUTED,
     "th_c": MUTED, "row_border": "1px solid #f1f5f9",
     "up": UP, "down": DOWN, "flat": "#cbd5e1",
     "reason_c": "#64748b", "badge_bg": "#eef2ff", "badge_fg": "#4338ca"}

TIERS = {
    "tier_a": ("🌟", "第一档 · 强势回踩", "回踩到位＋今日抗跌，可以分批慢慢买", "#2563eb", "#eff6ff"),
    "tier_b": ("🌱", "第二档 · 深度回踩", "先加自选观察，等企稳信号出现再动手", "#059669", "#ecfdf5"),
    "danger": ("🔥", "追高风险区", "涨太多了，现在进容易站岗", "#dc2626", "#fef2f2"),
}


def _idx_cards(idx):
    n = len(idx) or 1
    cells = []
    for d in idx:
        up = d["chg_today"] >= 0
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else MUTED)
        bgc = "#fef2f2" if up else "#ecfdf5"
        cells.append(
            f'<td width="{100 // n}%" style="padding:5px">'
            f'<div style="background:{bgc};border-radius:14px;padding:12px 6px;text-align:center">'
            f'<div style="color:#64748b;font-size:12px">{C.esc(d["name"])}</div>'
            f'<div style="font-size:19px;font-weight:800;color:{INK};margin:3px 0">{C.num(d["close"])}</div>'
            f'<span style="display:inline-block;background:#ffffffcc;border-radius:99px;padding:1px 9px;'
            f'font-size:12px;font-weight:700;color:{c}">{d["chg_today"]:+.2f}%</span></div></td>')
    return "<tr>" + "".join(cells) + "</tr>"


def _tier_card(key, rows):
    icon, title, desc, color, bg = TIERS[key]
    return (f"<div style='background:{bg};border-radius:16px;padding:16px 18px;margin:12px 0'>"
            f"<div style='margin-bottom:2px'><span style='font-size:15.5px;font-weight:800;color:{INK}'>{icon} {title}</span>"
            f"<span style='float:right;background:{color};color:#fff;border-radius:99px;"
            f"font-size:12px;font-weight:700;padding:2px 11px'>{len(rows)}</span></div>"
            f"<div style='color:#64748b;font-size:12.5px;margin-bottom:10px'>{desc}</div>"
            f"<div style='background:{CARD};border-radius:12px;padding:4px 8px'>"
            + C.stock_table(rows, T) + "</div></div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_fs": "14px"},
                         "还没有 AI 点评——填入 AGNES_API_KEY 后，这里每天自动生成。")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:{BG}">
<div style="padding:22px 8px;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%">

<tr><td style="background:{CARD};border-radius:20px;border:1px solid {BORDER};padding:24px 26px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td>
      <div style="font-size:25px;font-weight:900;color:{INK}">📊 今日加仓池</div>
      <div style="color:{MUTED};font-size:13px;margin-top:4px">{ctx['data_date']} · 核心池66只 · 基准 {C.esc(bench['name'])} {bench['chg_today']:+.2f}%</div>
    </td>
    <td align="right" valign="middle">
      <span style="background:#eef2ff;color:#4338ca;border-radius:99px;padding:7px 15px;font-size:12px;font-weight:700">
      第一档 {ctx['counts']['tier_a']} 只</span>
    </td>
  </tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px">{_idx_cards(idx)}</table>
</td></tr>

<tr><td style="height:12px;line-height:12px;font-size:0">&nbsp;</td></tr>

<tr><td>
  {_tier_card('tier_a', tiers.get('tier_a', []))}
  {_tier_card('tier_b', tiers.get('tier_b', []))}
  {_tier_card('danger', tiers.get('danger', []))}
</td></tr>

<tr><td style="height:12px;line-height:12px;font-size:0">&nbsp;</td></tr>

<tr><td style="background:{CARD};border-radius:20px;border:1px solid {BORDER};padding:18px 22px">
  <div style="font-size:15.5px;font-weight:800;color:{INK};margin-bottom:8px">🤖 AI 点评 <span style="font-size:11px;color:{MUTED};font-weight:500">by Agnes</span></div>
  {ai_body}
</td></tr>

<tr><td style="height:12px;line-height:12px;font-size:0">&nbsp;</td></tr>

<tr><td style="text-align:center;padding:4px 18px 10px">
  <div style="color:#a5b0c5;font-size:11px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
