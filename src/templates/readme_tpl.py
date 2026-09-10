#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑬ 工程文档：README.md 渲染风，徽章、代码块、列表条目"""
from . import common as C

BG, CARD, LINE, INK, MUT = "#ffffff", "#f6f8fa", "#d0d7de", "#1f2328", "#57606a"
BLUE, GREEN, RED = "#0969da", "#1a7f37", "#cf222e"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,Courier New,monospace"

T_CODE = {"fs": "12.5px", "cell_pad": "5px 6px", "th_fs": "11px",
          "name_c": BLUE, "text_c": "#24292f", "muted": MUT,
          "th_c": "#24292f", "row_border": f"1px solid {LINE}",
          "up": RED, "down": GREEN, "flat": MUT,
          "bar_track": "#d8dee4", "reason_c": "#57606a",
          "badge_bg": "#ddf4ff", "badge_fg": BLUE}


def _h(text):
    return (f"<div style='font-family:{MONO};font-weight:700;font-size:19px;color:{INK};"
            f"border-bottom:1px solid {LINE};padding-bottom:6px;margin:22px 0 10px'>{text}</div>")


def _h2(text):
    return (f"<div style='font-family:{MONO};font-weight:600;font-size:15px;color:{INK};"
            f"margin:16px 0 6px'>{text}</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    bench = ctx["bench"]
    y, m, d = ctx["data_date"].split("-")

    badges = (f"<code style='background:#ddf4ff;color:{BLUE};border-radius:99px;padding:2px 10px;"
              f"font-family:{MONO};font-size:11.5px;font-weight:600'>build: passing</code> "
              f"<code style='background:#dafbe1;color:{GREEN};border-radius:99px;padding:2px 10px;"
              f"font-family:{MONO};font-size:11.5px;font-weight:600'>pool: 66</code> "
              f"<code style='background:#ffebe9;color:{RED};border-radius:99px;padding:2px 10px;"
              f"font-family:{MONO};font-size:11.5px;font-weight:600'>danger: {ctx['counts']['danger']}</code>")

    code_block_lines = [
        f"$ ./scan --date {ctx['data_date']}",
        f"[idx ] " + " | ".join(f"{dd['name']} {dd['close']:,.2f} ({dd['chg_today']:+.2f}%)" for dd in idx),
        f"[pool] up={st['up']} down={st['down']} avg={st['avg']:+.2f}%",
        f"[tier] A={ctx['counts']['tier_a']} B={ctx['counts']['tier_b']} danger={ctx['counts']['danger']} watch={ctx['counts']['watch']}",
        f"status: OK (66/66 refreshed)",
    ]
    code_block = "<br>".join(
        f"<span style='color:{GREEN if 'OK' in l or l.startswith('$') else '#24292f'}'>{C.esc(l)}</span>"
        for l in code_block_lines)

    entries = "".join(
        f"<li style='margin:7px 0'><b>{C.esc(r['name'])}</b> <code style='font-family:{MONO};"
        f"background:{CARD};border-radius:4px;padding:1px 6px;font-size:11.5px'>{r['code']}</code><br>"
        f"<span style='color:#57606a;font-size:12.5px;line-height:1.7'>&gt; {C.esc(r.get('_reason') or '')}</span></li>"
        for r in ta)
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": "#24292f", "muted": MUT},
                         "> Warning: AGNES_API_KEY not set. AI section disabled.")

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{LINE}">
<div style="padding:20px 10px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="720" cellpadding="0" cellspacing="0" style="max-width:720px;width:100%;background:{BG};
       border:1px solid {LINE};border-radius:6px">

<tr><td style="padding:20px 26px 0">
  <div style="border-bottom:1px solid {LINE};padding-bottom:10px">
    <span style="font-size:23px;font-weight:700;color:{INK}">加仓池日报</span>
    <span style="font-family:{MONO};font-size:13px;color:{MUT}">&nbsp;&nbsp;v{y}.{m}.{d}</span><br>
    <span style="font-family:{MONO};font-size:12.5px;color:{MUT}">多书视角选股系统的每日构建报告</span>
  </div>
  <div style="margin:10px 0">{badges}</div>
</td></tr>

<tr><td style="padding:0 26px">
  {_h('## 📊 今日快照')}
  <div style="background:{CARD};border:1px solid {LINE};border-radius:6px;padding:12px 14px;
       font-family:{MONO};font-size:12.5px;line-height:1.9">{code_block}</div>

  {_h('## ✅ 第一档 candidates（可分批）')}
  <ul style='padding-left:18px;margin:0'>{entries or '<i>无</i>'}</ul>

  {_h('## ⏳ 第二档 watchlist')}
  {_h2('等待信号：<code style=\"font-family:%s;background:%s;padding:1px 6px;border-radius:4px\">放量止跌 + 收复MA20</code>' % (MONO, CARD))}
  <div style='line-height:2.3'>{''.join(f"<code style='font-family:{MONO};background:{CARD};border:1px solid {LINE};border-radius:6px;padding:2px 8px;margin:3px;font-size:12px'>{C.esc(r['name'])}&nbsp;{r['code']}</code>" for r in tb[:24]) or '<i>空</i>'}</div>

  {_h('## 🚫 追高风险 excluded')}
  <blockquote style="border-left:4px solid {RED};background:#ffebe9;margin:0;padding:8px 14px;border-radius:0 6px 6px 0;
        font-size:12.5px;color:#424a53">{"、".join(C.esc(r['name']) for r in dg) or '无'} —
   位置过高或放量冲高，本策略不追。</blockquote>

  {_h('## 🤖 AI notes')}
  <div style="background:{CARD};border:1px solid {LINE};border-radius:6px;padding:10px 14px;
       font-size:13px;line-height:1.8">{ai_body}</div>
</td></tr>

<tr><td style="padding:18px 26px 22px;border-top:1px solid {LINE};margin-top:14px">
  <div style="color:{MUT};font-size:10.5px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
