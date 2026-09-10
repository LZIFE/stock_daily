#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""① 经典深蓝金融（默认）：深色渐变头 + 玻璃指数卡 + 彩色分层卡"""
from . import common as C

TIERS = {
    "tier_a": ("🟢", "第一档 · 强势回踩", "趋势未破＋今日抗跌，回踩到位，可分批关注", "#2563eb", "#eff6ff"),
    "tier_b": ("⏳", "第二档 · 深度回踩", "值博率高，等放量止跌/收复5日线再动手", "#d97706", "#fffbeb"),
    "danger": ("⛔", "追高风险区", "位置过高或放量冲高，不建议现价加仓", "#dc2626", "#fef2f2"),
}

T = {"fs": "13px", "cell_pad": "7px 6px", "th_fs": "12px",
     "name_c": "#111827", "text_c": "#374151", "muted": "#9ca3af",
     "th_c": "#64748b", "row_border": "1px solid #f1f5f9",
     "up": "#dc2626", "down": "#059669", "flat": "#94a3b8",
     "reason_c": "#475569"}


def _index_cards(idx):
    n = len(idx) or 1
    cells = []
    for d in idx:
        c = T["up"] if d["chg_today"] > 0 else (T["down"] if d["chg_today"] < 0 else T["flat"])
        cells.append(
            f'<td width="{100 // n}%" style="padding:6px">'
            f'<div style="background:#ffffff1a;border-radius:12px;padding:12px 8px;text-align:center">'
            f'<div style="color:#93a4c8;font-size:12px;margin-bottom:4px">{C.esc(d["name"])}</div>'
            f'<div style="color:#fff;font-size:19px;font-weight:700">{C.num(d["close"])}</div>'
            f'<div style="color:{c};font-size:13px;font-weight:600;margin-top:3px">{d["chg_today"]:+.2f}%</div>'
            f'</div></td>')
    return "<tr>" + "".join(cells) + "</tr>"


def _tier_card(key, rows):
    icon, title, desc, color, bg = TIERS[key]
    return (f"<div style='border:1px solid #e2e8f0;border-left:4px solid {color};"
            f"border-radius:12px;background:{bg};padding:14px 16px;margin:12px 0'>"
            f"<div><span style='font-size:15px;font-weight:700;color:#111827'>{icon} {title}</span>"
            f"<span style='float:right;background:{color};color:#fff;border-radius:99px;"
            f"font-size:12px;font-weight:600;padding:2px 10px'>{len(rows)} 只</span></div>"
            f"<div style='color:#64748b;font-size:12px;margin-bottom:10px'>{desc}</div>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    b = C.TIERS if False else None  # noqa
    pills = "".join(
        f"<span style='display:inline-block;background:{TIERS[k][4]};border:1px solid {TIERS[k][3]}33;"
        f"border-radius:99px;padding:4px 14px;margin:0 4px;font-size:13px;color:{TIERS[k][3]};font-weight:600'>"
        f"{TIERS[k][1].split(' · ')[0]} {ctx['counts'][k]} 只</span>"
        for k in ("tier_a", "tier_b", "danger"))
    ai = C.ai_block(ctx["ai_text"], T,
                    "未配置 AGNES_API_KEY，本次为纯规则报告。<br>在 GitHub Secrets 填入密钥后，这里会自动变成 AI 盘后点评。")
    idx_rows = "".join(
        f"<tr><td>{d['name']}</td></tr>" for d in [])  # placeholder no-op

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#eef1f6">
<div style="padding:20px 8px;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%">
<tr><td style="background:#1e2b4d;background:linear-gradient(135deg,#141b2e 0%,#1e2b4d 55%,#27406e 100%);border-radius:16px 16px 0 0;padding:26px 28px 20px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td>
      <div style="color:#8fa3cf;font-size:12px;letter-spacing:3px">DAILY BRIEF · 多书视角选股系统</div>
      <div style="color:#fff;font-size:24px;font-weight:800;margin-top:4px">📈 A股可加仓池日报</div>
      <div style="color:#b7c5e4;font-size:13px;margin-top:6px">数据日期 {ctx['data_date']} ｜ 核心池 66 只 ｜ 新浪/东财日K</div>
    </td>
    <td align="right" valign="top"><span style="background:#ffffff22;border:1px solid #ffffff33;color:#dbe6ff;
         border-radius:99px;padding:6px 14px;font-size:12px">基准 {C.esc(bench['name'])} {bench['chg_today']:+.2f}%</span></td>
  </tr></table>
  <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:14px">{_index_cards(idx)}</table>
</td></tr>
<tr><td style="background:#fff;padding:24px 26px 8px;border-left:1px solid #e5e9f2;border-right:1px solid #e5e9f2">
  <div style="text-align:center;margin:0 0 4px">{pills}</div>
  <p style="color:#64748b;font-size:12px;line-height:1.7;margin:10px 0 4px">
    相对强度基准：<b>{C.esc(bench['name'])} {bench['chg_today']:+.2f}%</b>。
    第一档＝回踩到位且今日跑赢大盘；第二档＝深度回踩待企稳；另有 {ctx['counts']['watch']} 只处于正常观察区未列示。</p>
  {_tier_card('tier_a', tiers.get('tier_a', []))}
  {_tier_card('tier_b', tiers.get('tier_b', []))}
  {_tier_card('danger', tiers.get('danger', []))}
  <div style="background:#f7f8fd;background:linear-gradient(135deg,#f5f7ff,#fdf7ee);border:1px solid #e3e8f5;border-radius:12px;padding:16px 18px;margin:16px 0 8px">
    <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:8px">🤖 AI 盘后点评 <span style="font-size:11px;color:#94a3b8;font-weight:400">by Agnes</span></div>
    {ai}
  </div>
</td></tr>
<tr><td style="background:#f8fafc;border:1px solid #e5e9f2;border-top:none;border-radius:0 0 16px 16px;padding:16px 26px">
  <div style="color:#94a3b8;font-size:11px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
