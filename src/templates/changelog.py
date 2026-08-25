#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑪ 更新日志：GitHub Release 风格，changelog叙事组织数据"""
from . import common as C

BG, CARD, LINE, INK, MUT = "#f6f8fa", "#ffffff", "#d0d7de", "#1f2328", "#656d76"
GREEN, PURPLE, RED, BLUE = "#1a7f37", "#8250df", "#cf222e", "#0969da"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def _chip(name, code):
    return (f"<code style='background:{BG};border:1px solid {LINE};border-radius:6px;"
            f"padding:2px 7px;font-family:{MONO};font-size:12px;color:{INK};margin:2px 2px'>"
            f"{C.esc(name)}&nbsp;{code}</code>")


def _section(icon, title, color, inner):
    return (f"<div style='margin:16px 0 4px;font-size:14px;font-weight:600;color:{INK}'>"
            f"<span style='color:{color};font-family:{MONO}'>{icon}</span> {title}</div>"
            f"<div style='border-left:2px solid {LINE};padding-left:14px;margin-left:5px'>{inner}</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    y, m, d = ctx["data_date"].split("-")

    added = "".join(
        f"<div style='margin:7px 0'><b>{C.esc(r['name'])}</b> <span style='color:{MUT};font-family:{MONO};font-size:12px'>#{r['code']}</span><br>"
        f"<span style='font-size:12.5px;color:#424a53;line-height:1.6'>{C.esc(r.get('_reason') or '')}</span></div>"
        for r in ta[:8])
    changed = "".join(_chip(r["name"], r["code"]) for r in tb[:20]) or "<i>无</i>"
    removed = "".join(_chip(r["name"], r["code"]) for r in dg) or "<i>无</i>"
    def _nm(row):
        return f"{C.esc(row['name'])} {row['chg_today']:+.2f}%" if row else "—"
    stats_line = (f"池内 {st['up']} 涨 / {st['down']} 跌，平均 {st['avg']:+.2f}%；"
                  f"最强 {_nm(st.get('best'))}；最弱 {_nm(st.get('worst'))}")
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#424a53", "muted": MUT},
                         "<i>AGNES_API_KEY 未配置 — release notes 由规则引擎生成。</i>")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:22px 10px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:{CARD};
       border:1px solid {LINE};border-radius:10px">

<tr><td style="padding:18px 22px 0">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td><h1 style="margin:0;font-size:21px;color:{INK}">加仓池 · 每日更新日志</h1></td>
    <td align="right"><span style="background:{GREEN};color:#fff;border-radius:99px;padding:3px 11px;
        font-size:12px;font-weight:600">Latest</span></td>
  </tr></table>
  <div style="color:{MUT};font-family:{MONO};font-size:13px;margin:6px 0 10px">v{y}.{m}.{d}
    &nbsp;·&nbsp; <span style='background:#ddf4ff;border-radius:99px;padding:1px 9px;font-size:12px;color:{BLUE}'>
    pool-66</span></div>
</td></tr>

<tr><td style="padding:0 22px"><div style="border-bottom:1px solid {LINE}"></div></td></tr>

<tr><td style="padding:6px 22px 0">
  <p style="font-size:13px;color:#424a53;line-height:1.8;margin:10px 0">
    本期基于收盘数据自动发布。指数表现：{" / ".join(f"{C.esc(d2['name'])} <b>{d2['chg_today']:+.2f}%</b>" for d2 in idx)}。
    {stats_line}。</p>
  {_section("✶", f"New Features — 新晋关注（第一档 {len(ta)} 只）", GREEN,
      added or "<i>本期无新增</i>")}
  {_section("◈", f"Maintenance — 第二档观察池变动（{len(tb)} 只）", PURPLE,
      f"<div style='line-height:2.2'>{changed}</div><div style='font-size:12px;color:{MUT};margin-top:4px'>等放量止跌信号后升级至第一档</div>")}
  {_section("⚠", f"Deprecation — 追高风险预警（{len(dg)} 只）", RED,
      f"<div style='line-height:2.2'>{removed}</div><div style='font-size:12px;color:{MUT};margin-top:4px'>位置过高/放量冲高，暂不纳入加仓计划</div>")}
  {_section("◆", "Notes — AI 点评 by Agnes", BLUE, ai_body)}
</td></tr>

<tr><td style="padding:16px 22px 20px">
  <details style="color:{MUT};font-size:10.5px;line-height:1.7">{C.DISCLAIMER}</details>
  <div style="color:{MUT};font-size:10.5px;line-height:1.7;margin-top:4px">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
