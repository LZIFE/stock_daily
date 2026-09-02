#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模板共用原语：转义、涨跌色、进度条等"""
import html


def esc(s):
    return html.escape(str(s))


def chg(v, up="#dc2626", down="#059669", flat="#94a3b8", nd=2, bold=True, arrow=True):
    """涨跌幅片段（国内惯例红涨绿跌，颜色由主题传入）"""
    if v is None:
        return f'<span style="color:{flat}">—</span>'
    c = up if v > 0 else (down if v < 0 else flat)
    a = ("▲ " if v > 0 else ("▼ " if v < 0 else "")) if arrow else ""
    w = "font-weight:600;" if bold else ""
    return f'<span style="color:{c};{w}font-variant-numeric:tabular-nums">{a}{v:+.{nd}f}%</span>'


def num(v, nd=2):
    return f"{v:,.{nd}f}" if v is not None else "—"


def pos_bar(pos, low="#2563eb", mid="#d97706", high="#dc2626",
            track="#e5e7eb", txt="#6b7280", w=74):
    if pos is None:
        return "—"
    pos = max(0, min(100, pos))
    c = low if pos <= 35 else (mid if pos <= 70 else high)
    return (f"<div style='background:{track};border-radius:99px;height:7px;width:{w}px;margin:2px auto'>"
            f"<div style='background:{c};height:7px;width:{pos:.0f}%;border-radius:99px'></div></div>"
            f"<span style='font-size:11px;color:{txt};font-variant-numeric:tabular-nums'>{pos:.0f}%</span>")


HEADS = ["名称", "现价", "今日", "距MA20", "60日区间位置", "PE", "评分", "加仓逻辑"]
COL_W = ["15%", "8%", "10%", "10%", "13%", "7%", "6%", "31%"]


def stock_table(rows, t):
    """通用个股表。t: 主题字典
    若任一行带 _multi_total（多视角评分启用），自动追加「多视角」列（总分+档位徽章+建议仓位%）
    """
    if not rows:
        return (f"<div style='padding:14px;text-align:center;color:{t['muted']};"
                f"background:{t.get('empty_bg', '#f9fafb')};{t.get('empty_extra', '')}'>本档今日无标的</div>")
    show_multi = any(r.get("_multi_total") is not None for r in rows)
    if show_multi:
        heads = HEADS + ["多视角"]
        widths = COL_W + ["10%"]
        # 把「加仓逻辑」从 31% 缩到 23%，让出 8% 给多视角列
        widths[7] = "23%"
    else:
        heads, widths = HEADS, COL_W
    ths = "".join(
        f"<th style='padding:{t['cell_pad']};font-size:{t['th_fs']};color:{t['th_c']};"
        f"font-weight:{t.get('th_w', 500)};text-align:center;background:{t.get('th_bg', 'transparent')};"
        f"border-bottom:{t.get('th_border', '2px solid #e2e8f0')};{t.get('th_extra', '')}width:{w}'>{h}</th>"
        for h, w in zip(heads, widths))

    # 档位 → 徽章配色
    band_style = {
        "tier_a":    ("#059669", "#ecfdf5", "A档"),
        "tier_b":    ("#2563eb", "#eff6ff", "B档"),
        "watch":     ("#d97706", "#fffbeb", "观察"),
        "danger":    ("#dc2626", "#fef2f2", "追高"),
        "frozen":    ("#6b7280", "#f3f4f6", "冻结"),
        "excluded":  ("#6b7280", "#f3f4f6", "排除"),
    }

    trs = []
    for r in rows:
        name = (f"<div style='font-weight:{t.get('name_w', 600)};color:{t['name_c']}'>{esc(r['name'])}</div>"
                f"<div style='color:{t['muted']};font-size:11px'>{r['code']}</div>")
        score = r.get("score")
        badge = (f"<span style='display:inline-block;background:{t.get('badge_bg', '#111827')};"
                 f"color:{t.get('badge_fg', '#fff')};{t.get('badge_shape', 'border-radius:99px;')}"
                 f"padding:2px 8px;font-size:12px;font-weight:600'>{score}</span>" if score else "—")

        def cell(inner, extra=""):
            return (f"<td style='padding:{t['cell_pad']};text-align:center;color:{t['text_c']};"
                    f"font-variant-numeric:tabular-nums;border-bottom:{t['row_border']};{extra}'>{inner}</td>")

        # 多视角单元格: 总分 + 档位徽章 + 仓位%
        multi_cell = ""
        if show_multi:
            mt = r.get("_multi_total")
            mb = r.get("_multi_band")
            if mt is not None and mb:
                fg, bg, label = band_style.get(mb, ("#6b7280", "#f3f4f6", mb))
                veto_dot = ""
                vetoes = r.get("_multi_veto") or []
                if vetoes:
                    veto_dot = (f"<div style='color:#dc2626;font-size:10px;margin-top:2px;line-height:1.3'>"
                                f"⚠ {esc(vetoes[0])}</div>")
                cap = r.get("_position_cap")
                cap_line = (f"<div style='color:{t.get('muted', '#94a3b8')};font-size:10px;margin-top:1px'>"
                            f"仓位≤{cap:.0f}%</div>") if cap is not None else ""
                multi_cell = (
                    f"<td style='padding:{t['cell_pad']};text-align:center;border-bottom:{t['row_border']}'>"
                    f"<div style='font-weight:700;color:{t.get('text_c','#1e293b')};font-size:14px;"
                    f"font-variant-numeric:tabular-nums'>{mt:.0f}</div>"
                    f"<span style='display:inline-block;background:{bg};color:{fg};"
                    f"border-radius:99px;padding:1px 6px;font-size:10px;font-weight:600;margin-top:1px'>"
                    f"{label}</span>"
                    f"{cap_line}{veto_dot}</td>")
            else:
                multi_cell = (f"<td style='padding:{t['cell_pad']};text-align:center;border-bottom:{t['row_border']};"
                              f"color:{t.get('muted','#94a3b8')}'>—</td>")

        trs.append(
            "<tr>"
            f"<td style='padding:{t['cell_pad']};text-align:left;border-bottom:{t['row_border']}'>{name}</td>"
            + cell(num(r.get("close")))
            + cell(chg(r.get("chg_today"), t["up"], t["down"], t["flat"]))
            + cell(chg(r.get("vs_ma20"), t["up"], t["down"], t["flat"]))
            + f"<td style='text-align:center;border-bottom:{t['row_border']};padding:{t['cell_pad']}'>"
              f"{pos_bar(r.get('pos60'), t.get('bar_low', '#2563eb'), t.get('bar_mid', '#d97706'), t.get('bar_high', '#dc2626'), t.get('bar_track', '#e5e7eb'), t['muted'])}</td>"
            + cell(num(r.get("pe_now"), 1))
            + cell(badge)
            + f"<td style='padding:{t['cell_pad']} 8px;text-align:left;font-size:{t.get('reason_fs', '12px')};"
              f"color:{t.get('reason_c', '#475569')};line-height:1.5;border-bottom:{t['row_border']};"
              f"{t.get('reason_extra', '')}'>{esc(r.get('_reason') or '—')}</td>"
            + multi_cell
            + "</tr>")
    return (f"<table width='100%' cellpadding='0' cellspacing='0' "
            f"style='border-collapse:collapse;font-size:{t['fs']}'><thead><tr>{ths}</tr></thead>"
            f"<tbody>{''.join(trs)}</tbody></table>")


def ai_block(ai_text, t, empty_hint):
    if ai_text:
        body = esc(ai_text).replace("**", "").replace("\n", "<br>")
        inner = f"<div style='line-height:1.9;font-size:{t.get('ai_fs', '14px')};color:{t.get('ai_c', '#1e293b')}'>{body}</div>"
    else:
        inner = (f"<div style='color:{t.get('muted', '#94a3b8')};font-size:13px;"
                 f"line-height:1.8'>{empty_hint}</div>")
    return inner


DISCLAIMER = ("⚠️ 本邮件为程序化数据整理与规则筛选，不构成任何投资建议。市场有风险，决策需独立。<br>"
              "口径：MA20/MA60 为简单均线；60日区间位置＝现价在近60日高低点间的百分位；红涨绿跌。")


def base_ctx(ctx):
    """派生常用字段：基准、分档计数、池级统计"""
    idx = ctx.get("indices") or []
    ctx.setdefault("bench", idx[0] if idx else {"name": "-", "chg_today": 0})
    tiers = ctx["tiers"]
    ctx.setdefault("counts", {k: len(tiers.get(k, []))
                              for k in ("tier_a", "tier_b", "danger", "watch")})
    pool = [r for k in ("tier_a", "tier_b", "danger", "watch") for r in tiers.get(k, [])]
    chgs = [r.get("chg_today") or 0 for r in pool]

    def _row_by(v):
        return next((r for r in pool if (r.get("chg_today") or 0) == v), None)

    ta = tiers.get("tier_a", [])
    pes = [r["pe_now"] for r in ta if r.get("pe_now")]
    ctx["stats"] = {
        "n": len(chgs),
        "up": sum(1 for c in chgs if c > 0),
        "down": sum(1 for c in chgs if c < 0),
        "flat": sum(1 for c in chgs if c == 0),
        "avg": round(sum(chgs) / len(chgs), 2) if chgs else 0,
        "best": _row_by(max(chgs)) if chgs else None,
        "worst": _row_by(min(chgs)) if chgs else None,
        "ta_avg_pe": round(sum(pes) / len(pes), 1) if pes else None,
    }
    return ctx
