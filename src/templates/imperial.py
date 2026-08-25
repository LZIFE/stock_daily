#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑤ 红金研报风：券商研报质感，绛红头部+鎏金点缀，正式稳重"""
from . import common as C

SERIF = "Georgia,'Songti SC','STSong','SimSun',serif"
RED, GOLD, INK, MUTED = "#8e1616", "#c9a227", "#292524", "#8b7d6f"

T = {"fs": "13px", "cell_pad": "7px 6px", "th_fs": "12px",
     "name_c": INK, "text_c": "#44403c", "muted": MUTED,
     "th_c": RED, "row_border": "1px solid #f0e6d8", "th_border": f"2px solid {GOLD}",
     "up": "#c0392b", "down": "#1a6840", "flat": "#a8a29e",
     "reason_c": "#57534e", "badge_bg": RED, "badge_fg": "#fff",
     "bar_track": "#ede4d3"}

TIERS = {
    "tier_a": ("◆", "第一档 · 强势回踩", "趋势未破、回踩到位，可分批布局", GOLD, "#fdf9ef"),
    "tier_b": ("◇", "第二档 · 深度回踩", "耐心等待企稳信号，勿急于接筹", "#b45309", "#fdf6ee"),
    "danger": ("▣", "风险提示 · 追高区", "位置偏高或放量冲高，建议观望", RED, "#fdf2f2"),
}


def _idx_cards(idx):
    n = len(idx) or 1
    cells = []
    for d in idx:
        c = T["up"] if d["chg_today"] > 0 else (T["down"] if d["chg_today"] < 0 else MUTED)
        cells.append(
            f'<td width="{100 // n}%" style="padding:5px">'
            f'<div style="background:#fff;border-top:3px solid {GOLD};padding:12px 6px;text-align:center;'
            f'box-shadow:0 1px 3px #00000014">'
            f'<div style="color:{MUTED};font-size:12px">{C.esc(d["name"])}</div>'
            f'<div style="font-family:{SERIF};font-size:19px;font-weight:700;color:{INK};margin:4px 0">{C.num(d["close"])}</div>'
            f'<div style="color:{c};font-size:12.5px;font-weight:600">{d["chg_today"]:+.2f}%</div></div></td>')
    return "<tr>" + "".join(cells) + "</tr>"


def _tier_card(key, rows):
    icon, title, desc, color, bg = TIERS[key]
    return (f"<div style='border:1px solid #eee2cc;background:{bg};padding:14px 16px;margin:12px 0'>"
            f"<div><span style='font-family:{SERIF};font-size:15.5px;font-weight:700;color:{INK}'>"
            f"<span style='color:{color}'>{icon}</span> {title}</span>"
            f"<span style='float:right;color:{MUTED};font-size:12px'>{len(rows)} 只</span></div>"
            f"<div style='color:{MUTED};font-size:12px;margin:4px 0 10px'>{desc}</div>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": INK},
                         "（AGNES_API_KEY 未配置，AI 点评暂缺。配置后自动生成。）")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f3ede2">
<div style="padding:20px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:#fffdf8;border:1px solid #e7dbc4">

<tr><td style="background:linear-gradient(135deg,{RED} 0%,#b91c1c 100%);border-bottom:3px solid {GOLD};padding:24px 28px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td>
      <div style="color:#ffd98a;font-size:11px;letter-spacing:4px">EQUITY RESEARCH DAILY</div>
      <div style="font-family:{SERIF};color:#fff;font-size:25px;font-weight:700;margin-top:5px">A股可加仓池日报</div>
      <div style="color:#f3d9a4;font-size:12.5px;margin-top:5px">数据日期 {ctx['data_date']} ｜ 核心池 66 只 ｜ 多书视角评分体系</div>
    </td>
    <td align="right" valign="top"><span style="border:1px solid {GOLD};color:#ffe9b8;padding:5px 12px;font-size:12px">
      基准 {C.esc(bench['name'])} {bench['chg_today']:+.2f}%</span></td>
  </tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px">{_idx_cards(idx)}</table>
</td></tr>

<tr><td style="padding:20px 26px 8px">
  {_tier_card('tier_a', tiers.get('tier_a', []))}
  {_tier_card('tier_b', tiers.get('tier_b', []))}
  {_tier_card('danger', tiers.get('danger', []))}
  <p style="color:{MUTED};font-size:12px">另有 {ctx['counts']['watch']} 只处于常态观察区。</p>

  <div style="border:1px solid #eee2cc;border-top:3px solid {RED};padding:14px 18px;margin:14px 0 8px;background:#fffdf8">
    <div style="font-family:{SERIF};font-size:15px;font-weight:700;color:{INK};margin-bottom:6px">
      <span style="color:{RED}">▍</span>AI 盘后点评 <span style="font-size:11px;color:{MUTED};font-weight:400">by Agnes</span></div>
    {ai_body}
  </div>
</td></tr>

<tr><td style="background:#f7f1e5;border-top:1px solid #e7dbc4;padding:14px 26px">
  <div style="color:#a49a89;font-size:11px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
