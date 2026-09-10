#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""③ 极简杂志风：白底衬线、细分隔线、大留白，单一墨色点缀"""
from . import common as C

SERIF = "Georgia,Times New Roman,Songti SC,STSong,serif"
INK, MUTED, HAIR = "#111111", "#8a8a8a", "#e4e4e4"
UP, DOWN = "#9f1d1d", "#1a6840"

T = {"fs": "13px", "cell_pad": "8px 6px", "th_fs": "11px",
     "name_c": INK, "text_c": "#333333", "muted": MUTED,
     "th_c": MUTED, "row_border": f"1px solid {HAIR}",
     "up": UP, "down": DOWN, "flat": "#b5b5b5",
     "reason_c": "#555555", "reason_extra": "font-style:italic;",
     "badge_bg": "transparent", "badge_fg": INK,
     "badge_shape": "border:1px solid #cccccc;"}

SEC = {"tier_a": ("一", "强势回踩 · 可分批关注"),
       "tier_b": ("二", "深度回踩 · 等待企稳信号"),
       "danger": ("三", "追高风险区 · 现价不加仓")}


def _idx_row(idx):
    tds = ""
    for d in idx:
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else MUTED)
        tds += (f"<td style='padding:14px 10px;text-align:center;border-left:1px solid {HAIR}'>"
                f"<div style='font-size:11px;letter-spacing:2px;color:{MUTED}'>{C.esc(d['name'])}</div>"
                f"<div style='font-size:22px;color:{INK};margin:4px 0'>{d['close']:,.2f}</div>"
                f"<span style='color:{c};font-size:12px'>{d['chg_today']:+.2f}%</span></td>")
    return f"<tr>{tds}</tr>"


def _section(key, rows):
    no, title = SEC[key]
    return (f"<div style='margin:30px 0 10px'>"
            f"<div style='border-top:1px solid {INK};padding-top:8px'>"
            f"<span style='font-family:{SERIF};font-size:16px;font-weight:700;color:{INK}'>{no}&nbsp;·&nbsp;{title}</span>"
            f"<span style='float:right;color:{MUTED};font-size:12px'>{len(rows)} 只</span></div>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#222222", "muted": MUTED},
                         "AI 点评未启用（未配置 AGNES_API_KEY），当前为规则版报告。配置后此处自动更新。")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#ffffff">
<div style="padding:24px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%">

<tr><td style="text-align:center;padding:18px 0 0">
  <div style="font-size:11px;letter-spacing:6px;color:{MUTED}">DAILY BRIEF</div>
  <div style="font-family:{SERIF};font-size:30px;font-weight:700;color:{INK};margin:8px 0">可加仓池日报</div>
  <div style="color:{MUTED};font-size:12px">{ctx['data_date']}　·　核心池 66 只　·　基准 {C.esc(bench['name'])} {bench['chg_today']:+.2f}%</div>
</td></tr>
<tr><td style="border-top:3px solid {INK};border-bottom:1px solid {INK};margin-top:14px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td style="border-left:none"></td>{_idx_row(idx)}</tr></table>
</td></tr>

<tr><td style="padding:0 2px">
  {_section('tier_a', tiers.get('tier_a', []))}
  {_section('tier_b', tiers.get('tier_b', []))}
  {_section('danger', tiers.get('danger', []))}
  <p style="color:{MUTED};font-size:12px;margin:18px 0 0">另有 {ctx['counts']['watch']} 只处于正常观察区，未列入分档。</p>

  <div style="margin:28px 0 10px;border-top:1px solid {INK};padding-top:12px">
    <div style="font-family:{SERIF};font-size:16px;font-weight:700;color:{INK}">四 · AI 点评 <span style="font-weight:400;font-size:12px;color:{MUTED}">—— by Agnes</span></div>
    <div style="border-left:2px solid {INK};margin:10px 0;padding:2px 0 2px 16px">{ai_body}</div>
  </div>
</td></tr>

<tr><td style="border-top:1px solid {HAIR};padding:14px 0 20px">
  <div style="color:#b3b3b3;font-size:11px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
