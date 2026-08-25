#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑩ 数据驾驶舱：KPI磁贴网格 + 紧凑表格，管理后台质感"""
from . import common as C

BG, PANEL, LINE = "#0f172a", "#1e293b", "#334155"
CYAN, AMBER, GREEN, RED, TXT, MUT = "#22d3ee", "#fbbf24", "#34d399", "#f87171", "#e2e8f0", "#7c8db0"

T = {"fs": "12.5px", "cell_pad": "6px 5px", "th_fs": "11px",
     "name_c": TXT, "text_c": "#cbd5e1", "muted": MUT,
     "th_c": CYAN, "row_border": f"1px solid {LINE}",
     "up": RED, "down": GREEN, "flat": MUT,
     "bar_track": LINE, "reason_c": "#94a3b8",
     "badge_bg": "#164e63", "badge_fg": CYAN}


def _tile(label, value, color=CYAN, sub=""):
    return (f"<td width='25%' style='padding:4px'><div style='background:{PANEL};border:1px solid {LINE};"
            f"border-radius:10px;padding:12px 8px;text-align:center'>"
            f"<div style='font-size:11px;color:{MUT}'>{label}</div>"
            f"<div style='font-size:20px;font-weight:800;color:{color};margin-top:2px'>{value}</div>"
            + (f"<div style='font-size:10.5px;color:{MUT};margin-top:2px'>{sub}</div>" if sub else "")
            + "</div></td>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    best, worst = st.get("best"), st.get("worst")
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#cbd5e1", "muted": MUT},
                         "MODULE OFFLINE — 配置 AGNES_API_KEY 后启用AI模块。")

    def strip():
        segs = "".join(
            f"<span style='display:inline-block;background:{PANEL};border-radius:6px;padding:6px 10px;"
            f"margin:3px;font-size:12px;color:{TXT}'>{C.esc(d['name'])} "
            f"<b style='color:{RED if d['chg_today']>0 else GREEN}'>{d['chg_today']:+.2f}%</b></span>"
            for d in idx)
        return f"<div style='text-align:center;margin:10px 0'>{segs}</div>"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:18px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="700" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;background:{PANEL};
       border:1px solid {LINE};border-radius:14px">

<tr><td style="padding:14px 18px;border-bottom:1px solid {LINE}">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td><span style="color:{RED}">●</span><span style="color:{AMBER}"> ●</span><span style="color:{GREEN}"> ●</span>
      &nbsp;&nbsp;<b style="color:{TXT};font-size:15px">加仓池驾驶舱 · COCKPIT</b></td>
    <td align="right" style="color:{MUT};font-size:11.5px">DATA {ctx['data_date']}</td>
  </tr></table>
  {strip()}
</td></tr>

<tr><td style="padding:10px">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    {_tile('池内上涨', st['up'], RED)}{_tile('池内下跌', st['down'], GREEN)}
    {_tile('平均涨幅', f"{st['avg']:+.2f}%", CYAN)}{_tile('第一档', ctx['counts']['tier_a'], AMBER)}
  </tr><tr>
    {_tile('深度回踩', ctx['counts']['tier_b'], '#a78bfa')}
    {_tile('追高风险', ctx['counts']['danger'], RED)}
    {_tile('池内最强', (C.esc(best['name']) if best else '—'), RED,
           f"{best['chg_today']:+.2f}%" if best else '')}
    {_tile('池内最弱', (C.esc(worst['name']) if worst else '—'), GREEN,
           f"{worst['chg_today']:+.2f}%" if worst else '')}
  </tr></table>
</td></tr>

<tr><td style="padding:0 10px 6px">
  <div style="background:#0b1220;border:1px solid {LINE};border-radius:10px;padding:10px 12px;margin-bottom:8px">
    <div style="color:{CYAN};font-size:13px;font-weight:700;margin-bottom:4px">▍第一档 · 强势回踩（{ctx['counts']['tier_a']}）</div>
    {C.stock_table(tiers.get('tier_a', []), T)}
  </div>
  <div style="background:#0b1220;border:1px solid {LINE};border-radius:10px;padding:10px 12px;margin-bottom:8px">
    <div style="color:{AMBER};font-size:13px;font-weight:700;margin-bottom:4px">▍第二档 · 深度回踩（{ctx['counts']['tier_b']}）</div>
    {C.stock_table(tiers.get('tier_b', []), T)}
  </div>
  <div style="background:#0b1220;border:1px solid {LINE};border-radius:10px;padding:10px 12px">
    <div style="color:{RED};font-size:13px;font-weight:700;margin-bottom:4px">▍追高风险（{ctx['counts']['danger']}）</div>
    {C.stock_table(tiers.get('danger', []), T)}
  </div>
</td></tr>

<tr><td style="padding:10px">
  <div style="border:1px dashed {CYAN}55;border-radius:10px;padding:10px 14px">
    <div style="color:{CYAN};font-weight:700;font-size:13px;margin-bottom:4px">⌨ AI MODULE · AGNES</div>
    <div style="font-size:12.5px;line-height:1.8;color:{TXT}">{ai_body}</div>
  </div>
</td></tr>

<tr><td style="padding:4px 16px 16px;color:#526180;font-size:10.5px;line-height:1.7">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
