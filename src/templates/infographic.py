#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑳ 信息图数据新闻：大数字、双色堆叠条、占比可视化，图表叙事"""
from . import common as C

BG, CARD, INK, MUT, LINE = "#f7f7f4", "#ffffff", "#191919", "#737373", "#e3e3de"
BLUE, RED, GREEN = "#2f6fed", "#e0442c", "#1a9a6c"
SANS = "Helvetica Neue,Arial,PingFang SC,sans-serif"


def _big_num(value, label, color=INK):
    return (f"<td width='25%' style='padding:5px'><div style='background:{CARD};border:1px solid {LINE};padding:16px 8px'>"
            f"<div style='font-size:30px;font-weight:800;color:{color};line-height:1.1;"
            f"font-variant-numeric:tabular-nums'>{value}</div>"
            f"<div style='font-size:11.5px;color:{MUT};margin-top:4px'>{label}</div></div></td>")


def _dual_bar(up, down, total, labels=("上涨", "下跌")):
    up_pct = up / total * 100 if total else 50
    down_pct = 100 - up_pct
    return (f"<div style='margin:8px 0 4px'>"
            f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
            f"<td style='background:{RED};height:26px;width:{up_pct}%;text-align:right;padding-right:8px;"
            f"color:#fff;font-size:12px;font-weight:700;vertical-align:middle'>{labels[0]} {up}</td>"
            f"<td style='background:{GREEN};height:26px;width:{down_pct}%;text-align:left;padding-left:8px;"
            f"color:#fff;font-size:12px;font-weight:700;vertical-align:middle'>{labels[1]} {down}</td>"
            f"</tr></table></div>")


def _rank_bar(r, max_score):
    pct = int(r["score"] / (max_score or 100) * 100)
    return (f"<tr><td style='padding:8px 0;border-bottom:1px solid {LINE}'>"
            f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
            f"<td width='90'><b style='font-size:13.5px;color:{INK}'>{C.esc(r['name'])}</b><br>"
            f"<span style='font-size:10.5px;color:{MUT}'>{r['code']}</span></td>"
            f"<td><div style='background:{LINE};height:14px;border-radius:2px;margin:0 10px'>"
            f"<div style='width:{pct}%;height:14px;background:{BLUE};"
            f"background:linear-gradient(90deg,{BLUE},#7aa5f5);border-radius:2px'></div></div></td>"
            f"<td width='34' align='right'><b style='font-size:14px;color:{BLUE};"
            f"font-variant-numeric:tabular-nums'>{r['score']}</b></td></tr></table>"
            f"<div style='font-size:11.5px;color:{MUT};line-height:1.6;margin-top:3px'>{C.esc(r.get('_reason') or '')}</div>"
            f"</td></tr>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta = sorted(tiers.get("tier_a", []), key=lambda x: -x.get("score", 0))[:6]
    tb, dg = tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#333333", "muted": MUT},
                         "（数据来源：规则引擎。AGNES_API_KEY 配置后，本栏由 AI 撰写。）")

    # 池内涨跌分布
    dist = "".join(
        f"<td style='padding:5px;text-align:center;background:{CARD};border:1px solid {LINE}'>"
        f"<div style='font-size:20px;font-weight:800;color:{INK}'>{ctx['counts'][k]}</div>"
        f"<div style='font-size:11px;color:{MUT}'>{lbl}</div></td>"
        for k, lbl in (("tier_a", "第一档"), ("tier_b", "第二档"), ("danger", "追高风险"), ("watch", "观察区")))
    max_score = ta[0]["score"] if ta else 100
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:22px 10px;font-family:{SANS}">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="660" cellpadding="0" cellspacing="0" style="max-width:660px;width:100%">

<tr><td style="padding:8px 4px 14px">
  <div style="font-size:12px;font-weight:700;color:{BLUE};letter-spacing:2px">DATA STORY · 数据新闻</div>
  <div style="font-size:24px;font-weight:900;color:{INK};margin:4px 0;line-height:1.3">
   今天，你的股票池里发生了什么？</div>
  <div style="font-size:12px;color:{MUT}">{ctx['data_date']} · 样本：核心池66只 · 方法：多书视角评分</div>
</td></tr>

<tr><td>
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    {_big_num(f"{st['avg']:+.2f}%", "池内平均涨幅", RED if st['avg'] > 0 else GREEN)}
    {_big_num(st['n'], '覆盖标的')}
    {_big_num(f"{st['ta_avg_pe'] or '—'}", '第一档平均PE', BLUE)}
    {_big_num(ctx['counts']['tier_a'], '今日入选数')}
  </tr></table>
</td></tr>

<tr><td style="padding:12px 4px">
  <div style="background:{CARD};border:1px solid {LINE};padding:16px 18px">
    <div style="font-size:15px;font-weight:800;color:{INK};margin-bottom:2px">① 谁在涨，谁在跌？</div>
    <div style="font-size:12px;color:{MUT};margin-bottom:10px">池内 {st['n']} 只标的当日分布 · 红涨绿跌</div>
    {_dual_bar(st['up'], st['down'] + st['flat'], st['n'])}
    <div style="font-size:11.5px;color:{MUT};margin-top:6px">最强：{C.esc(st['best']['name']) if st.get('best') else '—'}
    　最弱：{C.esc(st['worst']['name']) if st.get('worst') else '—'}</div>
  </div>
</td></tr>

<tr><td style="padding:0 4px 12px">
  <div style="background:{CARD};border:1px solid {LINE};padding:16px 18px">
    <div style="font-size:15px;font-weight:800;color:{INK};margin-bottom:2px">② 四档结构</div>
    <div style="font-size:12px;color:{MUT};margin-bottom:8px">按策略分层的数量分布</div>
    <table width="100%" cellpadding="0" cellspacing="0"><tr>{dist}</tr></table>
  </div>
</td></tr>

<tr><td style="padding:0 4px 12px">
  <div style="background:{CARD};border:1px solid {LINE};padding:16px 18px">
    <div style="font-size:15px;font-weight:800;color:{INK};margin-bottom:2px">③ 第一档评分排行 TOP{len(ta)}</div>
    <div style="font-size:12px;color:{MUT};margin-bottom:4px">条形长度＝综合评分（满分100）</div>
    <table width="100%" cellpadding="0" cellspacing="0">{''.join(_rank_bar(r, max_score) for r in ta) or '<i>无</i>'}</table>
  </div>
</td></tr>

<tr><td style="padding:0 4px 12px">
  <div style="background:{CARD};border:1px solid {LINE};padding:16px 18px">
    <div style="font-size:15px;font-weight:800;color:{INK};margin-bottom:6px">④ 名单速览</div>
    <p style="font-size:12.5px;line-height:2;color:#404040;margin:0">
      <b style="color:{GREEN}">深水区（{len(tb)}）：</b>{"、".join(C.esc(r['name']) for r in tb[:12]) or "—"}<br>
      <b style="color:{RED}">高位勿追（{len(dg)}）：</b>{(C.esc(dg[0]['name']) if dg else "—")}{" 等" if len(dg)>1 else ""}<br>
      <span style="color:{MUT}">指数背景：{"；".join(f"{C.esc(d['name'])}{d['chg_today']:+.2f}%" for d in idx)}</span></p>
  </div>
</td></tr>

<tr><td style="padding:0 4px 12px">
  <div style="border:2px solid {BLUE};background:{CARD};padding:14px 18px">
    <div style="font-size:13px;font-weight:800;color:{BLUE};margin-bottom:4px">⑤ 记者手记 · BY AGNES</div>
    <div style="font-size:13px;line-height:1.9;color:#333333">{ai_body}</div>
  </div>
</td></tr>

<tr><td style="padding:6px 4px 14px;font-size:10px;color:#a3a39c;line-height:1.8;
      border-top:3px solid {INK}">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
