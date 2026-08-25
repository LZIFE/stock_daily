#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""报告组装：加仓逻辑生成 + 模板分发 + 邮件主题"""
import os

try:
    from .templates import LABELS, render as _render
except ImportError:  # 直接以脚本方式运行时
    from templates import LABELS, render as _render


# ---------- 加仓逻辑（规则自动生成，可解释、不编造）----------
def _reason(r, bench_chg):
    p = []
    ny = r.get("np_yoy")
    if ny is not None and ny >= 30:
        p.append(f"净利+{ny:.0f}%" + ("高增" if ny >= 100 else ""))
    pe = r.get("pe_now")
    if pe:
        p.append((f"PE{pe:.1f}" + ("低估" if pe <= 15 else ("合理" if pe <= 22 else ""))))
    v20 = r.get("vs_ma20")
    if v20 is not None:
        if -1 <= v20 <= 1:
            p.append("正踩MA20企稳")
        elif -7 <= v20 < -1:
            p.append(f"回踩至MA20下方{abs(v20):.0f}%")
    v60 = r.get("vs_ma60")
    if v60 is None:
        pass
    elif v60 > 0:
        p.append("站上MA60趋势完好")
    elif v60 >= -5:
        p.append("MA60附近有支撑")
    chg = r.get("chg_today")
    if chg is not None and bench_chg is not None:
        if chg > 0 and bench_chg <= -1:
            p.append("大盘重挫日逆势收红")
        elif chg >= bench_chg + 1:
            p.append("显著强于大盘")
    pos = r.get("pos60")
    if pos is not None and pos <= 20:
        p.append("处60日区间底部")
    return "·".join(p[:4])


def build_html(indices, tiers, ai_text, data_date, template=None):
    template = template or os.environ.get("REPORT_TEMPLATE", "vogue")
    bench_chg = indices[0]["chg_today"] if indices else 0
    for k in ("tier_a", "tier_b", "danger", "watch"):
        for r in tiers.get(k, []):
            r["_reason"] = _reason(r, bench_chg)
    ctx = {"indices": indices, "tiers": tiers, "ai_text": ai_text, "data_date": data_date}
    return _render(template, ctx)


def email_subject(indices, data_date):
    parts = " ".join(f"{d['name']}{d['chg_today']:+.2f}%" for d in indices[:2])
    flag = "🔴" if any(d["chg_today"] < -1 for d in indices) else "🟢"
    return f"{flag} A股加仓池日报 {data_date[5:]} | {parts}"
