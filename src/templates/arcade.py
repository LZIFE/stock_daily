#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⑱ 像素街机：Pico-8色板、方块血条、游戏UI叙事"""
from . import common as C

BG, INK = "#1a1c2c", "#f4f4f4"
RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, MUT = ("#ff004d", "#ffa300", "#ffec27",
                                                 "#00e436", "#29adff", "#7b25c8", "#5d648b")
MONO = "ui-monospace,Menlo,Consolas,'Courier New',monospace"


def _hp_bar(pos, color):
    pos = max(0, min(100, pos or 0))
    filled = int(pos / 10)
    return (f"<span style='font-family:{MONO};color:{color};font-size:13px;letter-spacing:1px'>"
            f"{'█' * filled}{'░' * (10 - filled)}</span> <span style='color:{MUT};font-size:11px'>{pos:.0f}%</span>")


def render(ctx):
    ctx = C.base_ctx(ctx)
    idx, tiers, st = ctx["indices"], ctx["tiers"], ctx["stats"]
    ta, tb, dg = tiers.get("tier_a", []), tiers.get("tier_b", []), tiers.get("danger", [])
    ai_body = C.ai_block(ctx["ai_text"], {"ai_c": INK, "muted": MUT},
                         "PRESS [AGNES_API_KEY] TO CONTINUE…")

    def player_card(r, i):
        colors = [GREEN, BLUE, YELLOW, PURPLE]
        c = colors[i % 4]
        return (f"<tr><td style='border:2px solid {c};border-radius:0;padding:9px 11px;margin:0;background:#24283f'>"
                f"<table width='100%' cellpadding='0' cellspacing='0'><tr>"
                f"<td><span style='font-family:{MONO};font-weight:800;font-size:14px;color:{INK}'>"
                f"P{i + 1}·{C.esc(r['name'])}</span> <span style='color:{MUT};font-size:11px'>{r['code']}</span></td>"
                f"<td align='right'><span style='font-family:{MONO};font-weight:800;font-size:13px;"
                f"color:{YELLOW if r['chg_today'] > 0 else BLUE}'>{r['chg_today']:+.2f}%</span></td></tr>"
                f"<tr><td colspan='2' style='padding-top:5px'>"
                f"<span style='font-size:12px;color:{MUT}'>HP(60D位)</span> {_hp_bar(r.get('pos60'), c)}"
                f"&nbsp;&nbsp;<span style='font-family:{MONO};font-size:12px;color:{ORANGE}'>SCORE {r['score']}</span>"
                f"</td></tr>"
                f"<tr><td colspan='2' style='font-size:11.5px;color:#9aa0c0;line-height:1.7;padding-top:3px'>"
                f"{C.esc(r.get('_reason') or '')}</td></tr></table></td></tr>"
                f"<tr><td style='height:7px;line-height:7px'></td></tr>")

    idx_row = "".join(
        f"<td width='25%' align='center' style='padding:4px'><div style='background:#24283f;border:2px solid "
        f"{PURPLE};padding:8px 2px'>"
        f"<div style='font-family:{MONO};font-size:10.5px;color:{MUT}'>{C.esc(d['name'])}</div>"
        f"<div style='font-family:{MONO};font-size:15px;font-weight:800;color:{INK}'>{C.num(d['close'])}</div>"
        f"<div style='font-family:{MONO};font-size:11px;color:{GREEN if d['chg_today']>0 else RED}'>{d['chg_today']:+.2f}%</div>"
        f"</div></td>" for d in idx)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:{BG}">
<div style="padding:20px 8px;font-family:-apple-system,'PingFang SC',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table width="660" cellpadding="0" cellspacing="0" style="max-width:660px;width:100%;background:#14162a;
       border:3px solid {PURPLE}">

<tr><td style="padding:18px 16px 8px;text-align:center">
  <div style="font-family:{MONO};font-weight:900;font-size:22px;color:{YELLOW};letter-spacing:2px">
   ★ POOL FIGHTER II ★</div>
  <div style="font-family:{MONO};font-size:11.5px;color:{MUT};margin-top:3px">
   加仓池日报 · ROUND {ctx['data_date'].replace('-', '.')} · INSERT COIN 🪙</div>
</td></tr>

<tr><td style="padding:8px 14px"><table width="100%" cellpadding="0" cellspacing="0"><tr>{idx_row}</tr></table></td></tr>

<tr><td style="padding:6px 14px">
  <div style="background:#24283f;border:2px dashed {BLUE};padding:9px 12px;margin-bottom:8px">
   <span style="font-family:{MONO};font-size:12.5px;color:{BLUE};font-weight:700">▶ BATTLE STATUS:</span>
   <span style="font-family:{MONO};font-size:12.5px;color:{INK}">
   &nbsp;WINNERS×{st['up']} LOSERS×{st['down']} AVG {st['avg']:+.2f}%</span></div>
</td></tr>

<tr><td style="padding:2px 14px 0">
  <div style="font-family:{MONO};font-size:14px;color:{GREEN};font-weight:900;margin-bottom:6px">
   ⚔ SELECT YOUR FIGHTER — 第一档（{len(ta)}）</div>
  <table width="100%" cellpadding="0" cellspacing="0">{''.join(player_card(r, i) for i, r in enumerate(ta))}</table>
</td></tr>

<tr><td style="padding:10px 14px 0">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td width="50%" valign="top" style="padding-right:4px">
      <div style="background:#24283f;border:2px solid {ORANGE};padding:9px 11px">
       <div style="font-family:{MONO};font-size:12px;color:{ORANGE};font-weight:800">💤 TRAINING ROOM ×{len(tb)}</div>
       <div style="font-size:11.5px;color:#9aa0c0;line-height:1.8;padding-top:4px">
        {"、".join(C.esc(r['name']) for r in tb[:10]) or '—'}</div></div>
    </td>
    <td width="50%" valign="top" style="padding-left:4px">
      <div style="background:#24283f;border:2px solid {RED};padding:9px 11px">
       <div style="font-family:{MONO};font-size:12px;color:{RED};font-weight:800">☠ GAME OVER ZONE ×{len(dg)}</div>
       <div style="font-size:11.5px;color:#9aa0c0;line-height:1.8;padding-top:4px">
        {(C.esc(dg[0]['name']) if dg else '—')} — 高位站岗警告</div></div>
    </td>
  </tr></table>
</td></tr>

<tr><td style="padding:12px 14px 4px">
  <div style="background:#24283f;border:2px solid {GREEN};padding:9px 12px">
   <div style="font-family:{MONO};font-size:12.5px;color:{GREEN};font-weight:800">🤖 NPC GUIDE · AGNES SAYS:</div>
   <div style="font-size:12.5px;color:{INK};line-height:1.8;padding-top:3px">{ai_body}</div></div>
</td></tr>

<tr><td style="padding:12px 16px 16px;text-align:center;font-family:{MONO};font-size:10px;color:#454a6b;
      line-height:1.8">{C.DISCLAIMER}</td></tr>
</table></td></tr></table></div></body></html>"""
