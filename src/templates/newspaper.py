#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""④ 报纸风：米色纸面、衬线密排、双线框，老牌财经报质感"""
from . import common as C

SERIF = "Georgia,Times New Roman,Songti SC,SimSun,serif"
PAPER, INK, RULE, MUTED = "#fbf7ee", "#1c1917", "#d8cdb4", "#78716c"
UP, DOWN = "#a51c1c", "#1a6840"

T = {"fs": "12px", "cell_pad": "5px 4px", "th_fs": "10.5px",
     "name_c": INK, "text_c": "#292524", "muted": MUTED,
     "th_c": INK, "row_border": f"1px solid #eee4cd", "th_border": "2px solid #1c1917",
     "up": UP, "down": DOWN, "flat": "#a8a29e",
     "reason_c": "#57534e", "reason_extra": f"font-family:{SERIF};font-style:italic;",
     "badge_bg": "#1c1917", "badge_fg": PAPER}

SEC = {"tier_a": ("■", "强势回踩 · 候选买入区"),
       "tier_b": ("■", "深度回踩 · 观察名单"),
       "danger": ("□", "追高风险 · 暂缓")}


def _strip(idx):
    segs = []
    for d in idx:
        c = UP if d["chg_today"] > 0 else (DOWN if d["chg_today"] < 0 else MUTED)
        segs.append(f"{C.esc(d['name'])}&nbsp;{d['close']:,.2f}&nbsp;<span style='color:{c}'>{d['chg_today']:+.2f}%</span>")
    return ("<div style='border-top:1px solid " + RULE + ";border-bottom:1px solid " + RULE +
            ";padding:8px 0;text-align:center;font-size:12.5px;color:" + INK + "'>"
            + "&nbsp;&nbsp;◆&nbsp;&nbsp;".join(segs) + "</div>")


def _section(key, rows):
    sq, title = SEC[key]
    return (f"<div style='margin:22px 0 6px'>"
            f"<div style='border-bottom:1px solid {INK};padding-bottom:4px;margin-bottom:6px'>"
            f"<span style='font-family:{SERIF};font-weight:700;font-size:15px;color:{INK}'>{sq} {title}</span>"
            f"<span style='float:right;font-size:11px;color:{MUTED};letter-spacing:1px'>{len(rows)} LISTED</span></div>"
            + C.stock_table(rows, T) + "</div>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, bench = ctx["indices"], ctx["tiers"], ctx["bench"]
    ai_body = C.ai_block(ctx["ai_text"], {"ai_fs": "13px", "ai_c": "#292524", "muted": MUTED},
                         "（电讯中断：AGNES_API_KEY 未配置。配置后此处自动刊出 AI 评论。）")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#efe9db">
<div style="padding:20px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="660" cellpadding="0" cellspacing="0" style="max-width:660px;width:100%;background:{PAPER};border:1px solid {RULE}">

<tr><td style="padding:20px 26px 12px;text-align:center;border-bottom:4px double {INK}">
  <div style="font-family:{SERIF};font-size:11px;letter-spacing:4px;color:{MUTED}">THE A-POOL TIMES</div>
  <div style="font-family:{SERIF};font-size:28px;font-weight:700;color:{INK};margin:6px 0">加仓池日报</div>
  <div style="font-size:11.5px;color:{MUTED}">{ctx['data_date']}（星期{('一二三四五六日'[__import__('datetime').datetime.now().weekday()])}）· 核心池 66 只 · 第 128 期</div>
</td></tr>

<tr><td style="padding:10px 26px 0">{_strip(idx)}</td></tr>

<tr><td style="padding:14px 26px">
  <p style="font-family:{SERIF};color:#44403c;font-size:13px;line-height:1.8;margin:0 0 6px">
    【本报讯】基准指数 {C.esc(bench['name'])} 收报 <b>{bench['close']:,.2f}</b>（{bench['chg_today']:+.2f}%）。
    经多书视角评分体系筛选，今日第一档候选 <b>{ctx['counts']['tier_a']} 只</b>，
    第二档观察 {ctx['counts']['tier_b']} 只，另有 {ctx['counts']['watch']} 只处于常态观察区。</p>
  {_section('tier_a', tiers.get('tier_a', []))}
  {_section('tier_b', tiers.get('tier_b', []))}
  {_section('danger', tiers.get('danger', []))}

  <div style="margin-top:20px;border:3px double {INK};padding:12px 16px">
    <div style="font-family:{SERIF};font-weight:700;font-size:14px;color:{INK};margin-bottom:6px">电讯 · AGNES 盘后评论</div>
    {ai_body}
  </div>
</td></tr>

<tr><td style="border-top:4px double {INK};padding:12px 26px 18px">
  <div style="color:#a8a29e;font-size:10.5px;line-height:1.8">{C.DISCLAIMER}</div>
</td></tr>
</table></td></tr></table></div></body></html>"""
