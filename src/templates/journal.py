#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑮ 手账涂鸦：纸面质感、楷体手写感、和纸胶带色条、贴纸标签"""
from . import common as C

PAPER, INK, MUT = "#fdfaf1", "#4a4238", "#a89c88"
KAI = "'Xingkai SC','STKaiti','KaiTi',Kaiti,cursive"
TAPE = ["#f9d5e533", "#d5f9e233", "#f9efd544", "#d5e2f933"]


def _entry(r, idx_n):
    tapes = ["#ffd6e0", "#c8f4de", "#ffe8b3", "#cde1ff"]
    tape = tapes[idx_n % 4]
    return f"""<div style="margin:14px 0;position:relative">
<div style="background:{tape}bb;display:inline-block;padding:2px 16px;border-radius:3px;
     font-family:{KAI};font-size:15px;color:#5b4a36;margin-bottom:-10px;margin-left:12px;
     box-shadow:0 1px 3px #00000018">✿ {C.esc(r['name'])}（{r['code']}）</div>
<div style="border:1.5px dashed #d8cbb2;background:#fffef9;border-radius:6px;padding:13px 15px">
  <div style="font-family:{KAI};font-size:14px;line-height:1.9;color:#5b5347">
   今天{'涨' if r['chg_today'] > 0 else '跌'}了 <b>{abs(r['chg_today']):.2f}%</b>，
   {C.esc(r.get('_reason') or '')}。<br>
   <span style="color:#b09a72">✎ 小记：</span>回踩就分批，破位就放手，别恋战。</div>
</div></div>"""


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#5b5347", "muted": MUT},
                         "（这一页留给 AI 写——配置 AGNES_API_KEY 后自动补上。）")
    y, m, d = ctx["data_date"].split("-")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#efe8d8">
<div style="padding:22px 10px;font-family:{KAI}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{PAPER};
       border-radius:8px;box-shadow:0 6px 24px #00000026">

<tr><td style="padding:22px 30px 0">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td>
      <span style="font-size:26px;color:{INK};font-weight:700">📖 加仓手帐</span>
      <span style="font-family:-apple-system,sans-serif;font-size:12px;color:{MUT}">&nbsp;&nbsp;{y}.{m}.{d}</span>
    </td>
    <td align="right">
      <span style="display:inline-block;background:#ffb3a7;border-radius:99px;padding:3px 12px;
            font-size:12px;color:#7a2d1f;font-weight:700;transform:rotate(3deg)">第 {ctx['counts']['tier_a']} 只入选 ✍</span>
    </td>
  </tr></table>
  <div style="height:3px;background:repeating-linear-gradient(90deg,#e8ddc4 0 8px,transparent 8px 14px);
        border-radius:99px;margin:12px 0"></div>
</td></tr>

<tr><td style="padding:0 30px">
  <div style="background:#fbf3df;border-radius:6px;padding:11px 14px;font-size:13.5px;line-height:2;color:#6b604c">
   🌤 今日天气（盘面）：{"；".join(f"{C.esc(dd['name'])} <b>{dd['chg_today']:+.2f}%</b>" for dd in idx)}。
   池子里的朋友们 {"几家欢喜几家愁" if ctx['stats']['down'] else "集体飘红"}。</div>
</td></tr>

<tr><td style="padding:6px 30px 0">
  <div style="font-size:17px;color:{INK};margin:10px 0 2px">❀ 今日翻牌（第一档）</div>
  {''.join(_entry(r, i) for i, r in enumerate(ta)) or '<div style="color:%s">今天没有新翻牌的，让钱包歇歇。</div>' % MUT}
</td></tr>

<tr><td style="padding:8px 30px 0">
  <div style="border:1.5px dashed #d8cbb2;background:#fefcf4;border-radius:6px;padding:11px 15px;
        font-size:13.5px;line-height:2;color:#6b604c">
   🌱 <b>蹲点观察</b>：{("、".join(C.esc(r['name']) for r in tb[:10])) or "—"}……
   它们在深水区，等一根放量大阳线就去接。<br>
   ⛔ <b>今日避雷</b>：{(C.esc(dg[0]['name']) if dg else "无")}{" 等" if len(dg) > 1 else ""}——涨太高的先不追啦。
  </div>
</td></tr>

<tr><td style="padding:14px 30px 0">
  <div style="background:#fff;border:2px solid #e8dcc0;border-radius:8px;padding:12px 16px">
   <div style="color:#b08d3e;font-size:14px;margin-bottom:4px">🤖 AI 小助手留言</div>
   <div style="font-size:13px;line-height:1.9;color:#5b5347">{ai_body}</div></div>
</td></tr>

<tr><td style="padding:16px 30px 22px;text-align:center">
  <div style="display:inline-block;background:#e25c4a;color:#fff;border-radius:4px;
        padding:5px 10px;font-size:11px;transform:rotate(-2deg)">今日份提醒 · 投资有风险</div>
  <div style="color:{MUT};font-size:10.5px;line-height:1.8;margin-top:8px">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
