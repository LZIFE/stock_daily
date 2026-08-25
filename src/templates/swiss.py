#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑦ 瑞士网格风：Helvetica、无圆角、粗黑规则线、超大数字，国际主义海报感"""
from . import common as C

HELV = "'Helvetica Neue',Helvetica,Arial,'PingFang SC','Microsoft YaHei',sans-serif"
BLACK, WHITE, YELLOW, MUTED = "#000000", "#ffffff", "#ffd400", "#6b7280"
UP, DOWN = "#d92d0f", "#0a7d32"

T = {"fs": "13px", "cell_pad": "7px 6px", "th_fs": "11px",
     "name_c": BLACK, "text_c": "#111111", "muted": MUTED,
     "th_c": WHITE, "th_bg": BLACK, "th_border": "2px solid #000000", "th_extra": "letter-spacing:1px;",
     "row_border": "1px solid #000000",
     "up": UP, "down": DOWN, "flat": MUTED,
     "reason_c": "#333333", "badge_shape": "", "badge_bg": YELLOW, "badge_fg": BLACK}


def _idx_grid(idx):
    n = len(idx) or 1
    cells = []
    for d in idx:
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else MUTED)
        cells.append(
            f'<td width="{100 // n}%" style="border:2px solid {BLACK};border-right-width:{1 if d is not idx[-1] else 2}px;'
            f'padding:12px 8px;text-align:left;vertical-align:top">'
            f'<div style="font-size:10px;letter-spacing:2px;color:{MUTED};text-transform:uppercase">{C.esc(d["name"])}</div>'
            f'<div style="font-size:26px;font-weight:800;color:{BLACK};line-height:1.15;margin:4px 0">{d["close"]:,.0f}<span style="font-size:13px;font-weight:600">.{str(f"{d['close']:.2f}").split(".")[1]}</span></div>'
            f'<div style="display:inline-block;background:{c};color:#fff;padding:1px 8px;font-size:12px;font-weight:700">{d["chg_today"]:+.2f}%</div></td>')
    return "<tr>" + "".join(cells) + "</tr>"


def _section(key, rows):
    meta = {"tier_a": ("01", "强势回踩 / BUY THE DIP · STRONG", YELLOW),
            "tier_b": ("02", "深度回踩 / WAIT FOR BASE", "#e5e7eb"),
            "danger": ("03", "追高风险 / OVERHEAT", "#fecaca")}
    no, title, chip = meta[key]
    return (f"<div style='margin:18px 0'>"
            f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
            f"<td style='background:{chip};border:2px solid {BLACK};padding:6px 12px'>"
            f"<span style='font-size:14px;font-weight:900;color:{BLACK}'>{no}&nbsp;&nbsp;{title}</span>"
            f"<span style='float:right;font-size:13px;font-weight:900;color:{BLACK}'>{len(rows)}</span></td></tr></table>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#111111"},
                         "AI COMMENTARY OFFLINE — 配置 AGNES_API_KEY 后自动启用。")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#fff">
<div style="padding:20px 10px;font-family:{HELV}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:#fff">

<tr><td style="padding:16px 0 12px;border-bottom:4px solid {BLACK}">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td>
      <div style="font-size:34px;font-weight:900;color:{BLACK};letter-spacing:-1px;line-height:1.05">加仓池<br>日报<sup style="font-size:12px;color:{UP}">●</sup></div>
    </td>
    <td valign="bottom" align="right" style="padding-bottom:4px">
      <div style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;text-align:right">
        A-POOL DAILY BRIEF<br>DATA&nbsp;{ctx['data_date']}<br>POOL&nbsp;66&nbsp;/&nbsp;SCORED&nbsp;20-BOOKS</div>
    </td>
  </tr></table>
</td></tr>

<tr><td style="padding:14px 0 0"><table width="100%" cellpadding="0" cellspacing="0">{_idx_grid(idx)}</table>
  <div style="border:2px solid {BLACK};border-top:none;padding:8px 12px;font-size:12.5px;color:{BLACK}">
    基准指数 <b>{C.esc(bench['name'])}</b> 收报 <b>{bench['close']:,.2f}</b>（{bench['chg_today']:+.2f}%）。
    分层：第一档 <b>{ctx['counts']['tier_a']}</b>／第二档 {ctx['counts']['tier_b']}／追高 {ctx['counts']['danger']}／观察 {ctx['counts']['watch']}。</div>
</td></tr>

<tr><td style="padding:10px 0 0">
  {_section('tier_a', tiers.get('tier_a', []))}
  {_section('tier_b', tiers.get('tier_b', []))}
  {_section('danger', tiers.get('danger', []))}
</td></tr>

<tr><td style="margin-top:6px;border:2px solid {BLACK};padding:12px 16px">
  <div style="font-size:13px;font-weight:900;color:{BLACK};margin-bottom:6px">04&nbsp;&nbsp;AI COMMENTARY <span style="font-weight:400;font-size:11px;color:{MUTED}">/ BY AGNES</span></div>
  {ai_body}
</td></tr>

<tr><td style="border-top:4px solid {BLACK};margin-top:14px;padding:10px 0 16px">
  <div style="color:{MUTED};font-size:10.5px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
