#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑧ 今日聚焦：只深读第一档Top3，大卡片叙事，其余速览"""
from . import common as C

INK, MUTED, LINE = "#0f172a", "#64748b", "#e2e8f0"
UP, DOWN = "#dc2626", "#059669"


def _kv(label, value, color=INK):
    return (f"<td style='text-align:center;padding:8px 4px;background:#f8fafc;border-radius:8px'>"
            f"<div style='font-size:11px;color:{MUTED}'>{label}</div>"
            f"<div style='font-size:15px;font-weight:700;color:{color};margin-top:2px'>{value}</div></td>")


def _hero_card(r, rank):
    chg_c = UP if r["chg_today"] > 0 else DOWN
    return f"""<div style="border:1px solid {LINE};border-radius:14px;padding:18px 20px;margin:12px 0;background:#fff">
<div style="margin-bottom:6px">
  <span style="background:{INK};color:#fff;border-radius:6px;padding:2px 10px;font-size:12px;font-weight:700">NO.{rank}</span>
  <span style="font-size:22px;font-weight:800;color:{INK};margin-left:10px">{C.esc(r['name'])}</span>
  <span style="color:{MUTED};font-size:13px">{r['code']}</span>
  <span style="float:right;font-size:16px;font-weight:700;color:{chg_c}">{r['chg_today']:+.2f}%</span>
</div>
<table width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0"><tr>
{_kv('现价', f"{r['close']:.2f}")}{_kv('PE', f"{r['pe_now']:.1f}" if r.get('pe_now') else '—')}
{_kv('净利同比', f"+{r['np_yoy']:.0f}%", UP)}{_kv('距MA20', f"{r['vs_ma20']:+.1f}%")}
{_kv('60日位', f"{r['pos60']:.0f}%")}{_kv('评分', r['score'], '#2563eb')}
</tr></table>
<div style="border-left:3px solid #2563eb;padding:6px 12px;background:#f0f6ff;border-radius:0 8px 8px 0;
     font-size:13px;line-height:1.7;color:#334155"><b>为什么值得关注：</b>{C.esc(r.get('_reason') or '')}。
     操作思路：回踩MA20附近分批，跌破MA60止损，不追盘中冲高。</div>
</div>"""


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers = ctx["indices"], ctx["tiers"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: (-x.get("score", 0), -(x.get("vs_ma60") or -99)))
    top3 = ta[:3]
    rest = ta[3:]
    bench = ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#334155", "muted": MUTED},
                         "AI 深度解读待启用（配置 AGNES_API_KEY）。")
    hero = "".join(_hero_card(r, i + 1) for i, r in enumerate(top3)) or \
        "<p style='color:#94a3b8;text-align:center'>今日第一档无标的</p>"
    rest_html = "　".join(f"<span style='display:inline-block;background:#f1f5f9;border-radius:99px;"
                         f"padding:4px 12px;margin:3px;font-size:12.5px;color:#334155'>"
                         f"<b>{C.esc(r['name'])}</b>&nbsp;{r['chg_today']:+.2f}%</span>" for r in rest) or "—"
    strip = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(
        f"{C.esc(d['name'])} <b style='color:{UP if d['chg_today']>0 else DOWN}'>{d['chg_today']:+.2f}%</b>"
        for d in idx)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#e9edf3">
<div style="padding:20px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%">

<tr><td style="padding:6px 4px 12px">
  <div style="color:{MUTED};font-size:12px;letter-spacing:2px">FOCUS EDITION · 每日三只深读</div>
  <div style="font-size:26px;font-weight:900;color:{INK};margin-top:2px">今日聚焦 🔍</div>
  <div style="color:{MUTED};font-size:12.5px;margin-top:4px">{ctx['data_date']}｜{strip}</div>
</td></tr>

<tr><td>{hero}</td></tr>

<tr><td style="padding:6px 2px">
  <div style="font-size:13px;font-weight:700;color:{INK};margin:10px 0 6px">其余第一档候选（{len(rest)}）</div>
  <div>{rest_html}</div>
  <div style="font-size:13px;font-weight:700;color:{INK};margin:16px 0 6px">第二档观察（{ctx['counts']['tier_b']}）与风险区（{ctx['counts']['danger']}）</div>
  <div style="font-size:12.5px;color:{MUTED};line-height:1.7">深度回踩池有 {ctx['counts']['tier_b']} 只等待企稳信号；追高风险区 {ctx['counts']['danger']} 只建议回避。
  基准 {C.esc(bench['name'])} {bench['chg_today']:+.2f}%，完整数据见随附表格版。</div>
</td></tr>

<tr><td style="background:{INK};border-radius:14px;padding:14px 18px;margin:12px 0">
  <div style="color:#93c5fd;font-size:12px;letter-spacing:2px;margin-bottom:6px">AI DEEP READ · BY AGNES</div>
  <div style="color:#e2e8f0;font-size:13px;line-height:1.8">{ai_body}</div>
</td></tr>

<tr><td style="padding:14px 4px;color:#a3aec2;font-size:11px;line-height:1.8">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
