#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑫ 晨报简报：Morning Brew式活泼新闻信，大标题+分块短评"""
from . import common as C

INK, YELLOW, BLUE, RED, GREEN = "#111111", "#ffd60a", "#2563eb", "#e63946", "#2a9d8f"
MUT, LINE = "#6c757d", "#e9ecef"


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench, st = ctx["indices"], ctx["tiers"], ctx["bench"], ctx["stats"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))
    tb, dg = tiers.get("tier_b", []), tiers.get("danger", [])
    best = st.get("best")

    def stock_blurb(r):
        return (f"<div style='background:#fff;border:2px solid {INK};border-radius:12px;"
                f"padding:12px 14px;margin:8px 0;box-shadow:4px 4px 0 {INK}'>"
                f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
                f"<td><span style='font-size:17px;font-weight:900;color:{INK}'>{C.esc(r['name'])}</span>"
                f"<span style='color:{MUT};font-size:12px'>　{r['code']}</span></td>"
                f"<td align='right'><span style='background:{YELLOW};border-radius:99px;padding:2px 10px;"
                f"font-size:13px;font-weight:800;color:{INK}'>评分 {r['score']}</span></td></tr></table>"
                f"<div style='font-size:12.5px;color:#374151;line-height:1.7;margin-top:5px'>"
                f"今日 <b style='color:{RED if r['chg_today']>0 else GREEN}'>{r['chg_today']:+.2f}%</b>，"
                f"{C.esc(r.get('_reason') or '')}。</div></div>")

    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": INK, "muted": MUT},
                         "AI 专栏还在充电（缺 AGNES_API_KEY），明天见。")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{LINE}">
<div style="padding:20px 10px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%">

<tr><td style="padding:14px 4px">
  <div style="display:inline-block;background:{YELLOW};padding:2px 8px;font-size:13px;font-weight:800;color:{INK}">DAILY ☕</div>
  <span style="font-size:30px;font-weight:900;color:{INK};margin-left:8px">加仓池晨报</span>
  <div style="color:{MUT};font-size:12.5px;margin-top:4px">{ctx['data_date']} · 星期{'一二三四五六日'[__import__('datetime').date.fromisoformat(ctx['data_date']).weekday()]} ·
   你的机器人编辑又上线了</div>
</td></tr>

<tr><td style="background:{INK};border-radius:14px;padding:16px 18px;margin:6px 0">
  <div style="color:{YELLOW};font-size:13px;font-weight:800;letter-spacing:1px;margin-bottom:6px">⚡ 30秒看懂今天</div>
  <div style="color:#f8f9fa;font-size:14px;line-height:1.9">{"，".join(f"{C.esc(d['name'])}<b>{d['chg_today']:+.2f}%</b>" for d in idx)}。
  池内平均 <b>{st['avg']:+.2f}%</b>（{st['up']}涨/{st['down']}跌）。
  {('今天最靓的仔是 ' + C.esc(best['name']) + f"（{best['chg_today']:+.2f}%）。") if best else ''}</div>
</td></tr>

<tr><td style="padding:16px 2px 0">
  <div style="font-size:19px;font-weight:900;color:{BLUE};margin-bottom:2px">💎 第一档精选</div>
  <div style="font-size:12.5px;color:{MUT};margin-bottom:6px">回踩到位＋今天还扛住了大盘的考验</div>
  {''.join(stock_blurb(r) for r in ta[:5]) or "<i style='color:%s'>今日空仓候选，休息。</i>" % MUT}
</td></tr>

<tr><td style="padding:12px 2px 0">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="50%" valign="top" style="padding-right:5px">
      <div style="background:#fff;border-radius:12px;padding:12px 14px;border:1px solid #dee2e6">
        <div style="font-weight:800;color:{GREEN};margin-bottom:4px">🌱 深水区观察 ×{len(tb)}</div>
        <div style="font-size:12px;color:#495057;line-height:1.9">{"、".join(C.esc(r['name']) for r in tb[:10]) or "—"}<br>
        <span style="color:{MUT}">等一根放量阳线再谈感情。</span></div>
      </div>
    </td>
    <td width="50%" valign="top" style="padding-left:5px">
      <div style="background:#fff;border-radius:12px;padding:12px 14px;border:1px solid #dee2e6">
        <div style="font-weight:800;color:{RED};margin-bottom:4px">🔥 别追榜 ×{len(dg)}</div>
        <div style="font-size:12px;color:#495057;line-height:1.9">{"、".join(C.esc(r['name']) for r in dg) or "—"}<br>
        <span style="color:{MUT}">让子弹飞一会儿。</span></div>
      </div>
    </td>
  </tr></table>
</td></tr>

<tr><td style="padding:14px 2px 0">
  <div style="border:2px dashed {BLUE};border-radius:14px;padding:12px 16px">
    <div style="font-weight:900;color:{BLUE};margin-bottom:4px">🎙 AI 脱口秀 · by Agnes</div>
    <div style="font-size:13px;line-height:1.8;color:#343a40">{ai_body}</div>
  </div>
</td></tr>

<tr><td style="padding:14px 4px 8px;color:#adb5bd;font-size:10.5px;line-height:1.7">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
