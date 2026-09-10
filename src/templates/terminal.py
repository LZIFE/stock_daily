#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""② 终端暗黑风：Bloomberg终端质感，黑底等宽字体，扫描线分隔"""
from . import common as C

TIERS = {
    "tier_a": ("▣", "BUY-ZONE / 强势回踩", "TREND OK + RELATIVE STRENGTH, 分批关注", "#22c55e", "#0c150d"),
    "tier_b": ("▢", "WATCH / 深度回踩", "WAIT FOR STABILIZE SIGNAL, 等企稳", "#eab308", "#15130a"),
    "danger": ("✕", "OVERHEAT / 追高风险", "EXTENDED POSITION, 不建议现价加仓", "#ef4444", "#170b0b"),
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,Courier New,monospace"
UP, DOWN, FLAT = "#ff5c5c", "#35d07f", "#4b5f4b"
GREEN, DIM, LINE = "#22c55e", "#6f8f6f", "#1d2b1d"

T = {"fs": "12.5px", "cell_pad": "6px 5px", "th_fs": "11px",
     "name_c": "#d1fae5", "text_c": "#9fb8a4", "muted": "#54705c",
     "th_c": GREEN, "row_border": f"1px dashed {LINE}",
     "up": UP, "down": DOWN, "flat": FLAT,
     "bar_track": LINE, "reason_c": "#7ba05b",
     "badge_bg": "#132a17", "badge_fg": GREEN}


def _idx_line(idx):
    segs = []
    for d in idx:
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else FLAT)
        segs.append(f"{C.esc(d['name'])} <span style='color:#e5efe5'>{d['close']:,.2f}</span> "
                    f"<span style='color:{c}'>{d['chg_today']:+.2f}%</span>")
    return ("<div style='border:1px solid " + LINE + ";background:#0a120a;padding:10px 14px;"
            "font-size:13px;letter-spacing:0.5px'>" + "&nbsp;&nbsp;│&nbsp;&nbsp;".join(segs) + "</div>")


def _tier_card(key, rows):
    icon, title, desc, color, bg = TIERS[key]
    return (f"<div style='border:1px solid {LINE};border-left:3px solid {color};background:{bg};"
            f"padding:12px 14px;margin:12px 0'>"
            f"<div style='color:{color};font-weight:700;font-size:14px'>{icon} {title}"
            f"<span style='float:right;color:{DIM};font-size:11px'>[{len(rows)}]</span></div>"
            f"<div style='color:{DIM};font-size:11px;margin-bottom:8px'>{desc}</div>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    bar = "═" * 62
    ai = C.ai_block(ctx["ai_text"], T,
                    "> AGNES_API_KEY 未配置，本次输出规则版报告。<br>> 配置密钥后此处自动升级为AI点评。")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#050807">
<div style="padding:20px 8px;font-family:{MONO}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:#070b07;border:1px solid {LINE};border-radius:6px">

<tr><td style="padding:18px 20px 12px;border-bottom:2px solid {GREEN}33">
  <div style="color:{DIM};font-size:11px">{bar}</div>
  <div style="color:{GREEN};font-size:20px;font-weight:700;margin:8px 0 4px">A-POOL TERMINAL <span style="font-size:13px;color:#d1fae5">A股可加仓池日报</span></div>
  <div style="color:{DIM};font-size:12px">DATA {ctx['data_date']} · POOL 66 · SRC SINA/EM &nbsp;|&nbsp; BENCH {C.esc(bench['name'])} <span style='color:{FLAT}'>{bench['chg_today']:+.2f}%</span></div>
  <div style="margin-top:12px">{_idx_line(idx)}</div>
</td></tr>

<tr><td style="padding:16px 20px">
  {_tier_card('tier_a', tiers.get('tier_a', []))}
  {_tier_card('tier_b', tiers.get('tier_b', []))}
  {_tier_card('danger', tiers.get('danger', []))}
  <div style="border:1px solid {LINE};background:#0a120a;padding:12px 14px;margin-top:12px">
    <div style="color:{GREEN};font-size:13px;font-weight:700;margin-bottom:6px">&gt;&gt; AGNES COMMENTARY</div>
    {ai}
  </div>
</td></tr>

<tr><td style="padding:12px 20px 16px;border-top:1px solid {LINE}">
  <div style="color:#3f5643;font-size:10.5px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
