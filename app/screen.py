"""全市场榜单 + 决策日志。

两者合起来把系统从「单只分析器」变成「闭环」：
    榜单（看全市场）→ 单只深读 → 记入日志 → 事后自动复盘

**命名与呈现的诚实性要求**（这不是文案问题，它决定用户怎么用它）：
  · 榜单叫「低踩雷概率清单」，不叫「推荐买入」
    证据是 BUY 组坏率 4.52% vs 基准 11.14% —— 这是**避雷**的证据，不是收益的
  · 每条都带并列只数与该桶历史坏率
  · 日志的成败判据是**系统自己的承诺**（60 日内是否跌超 20%），
    **不是收益率** —— 收益维度实测无证据，拿它当判据等于把没证据的东西包装成有证据
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .paths import ALL_STOCKS_JSON, APP_DATA

JOURNAL_FILE = "journal.json"

# ---------------------------------------------------------------- 榜单定义
# 每种榜单：(标题, 一句话说明, 排序键, 是否升序)
KINDS = {
    "low_risk": (
        "低踩雷概率",
        "核心分最高的那批。这不是推荐买入清单 —— 它的证据在避雷，不在收益。",
        "core_score", False),
    "divergence": (
        "核心 4 本最看好",
        "核心 4 本远比其余 28 本看好。分歧的含义未经回测验证。",
        "divergence", False),
    "divergence_neg": (
        "核心 4 本最看空",
        "核心 4 本远比其余 28 本看空。",
        "divergence", True),
    "rise": (
        "分数近期上行",
        "近 3 期核心分上升最多。分数变化本身未经回测验证。",
        "delta3", False),
    "fall": (
        "分数近期下行",
        "近 3 期核心分下降最多。",
        "delta3", True),
    "high_risk": (
        "踩雷概率最高",
        "核心分最低的那批。历史坏率最高，用于反面参考。",
        "core_score", True),
}

DISCLAIMER = (
    "榜单按核心分排序，而核心分没有收益预测能力"
    "（净选择效应 +0.038pp/月，95% 区间跨 0，现实费率下被交易成本吃光）。"
    "它的证据在尾部风险：高分桶「未来 60 日跌超 20%」的概率显著低于低分桶。"
    "请把它当作低踩雷概率清单，不是买入推荐。"
)

_TIE_BREAK = {
    "low_risk": ("divergence", False),
    "divergence": ("core_score", False),
    "divergence_neg": ("core_score", False),
    "rise": ("core_score", False),
    "fall": ("core_score", False),
    "high_risk": ("divergence", True),
}
_TIE_LABEL = {"divergence": "分歧（核心 4 本 − 其余 28 本）", "core_score": "核心分"}


def _industries():
    """代码 → 行业标签。_all_stocks.json 只覆盖约 35%，缺失的返回空。"""
    try:
        raw = json.loads(ALL_STOCKS_JSON.read_text(encoding="utf-8"))
        return {c: (v.get("sectors") or []) for c, v in raw.items()}
    except Exception:
        return {}


def _delta3(hist, code):
    """近 3 期核心分变化（面板最后一期是 2026-07-31，即最近一个季度）。"""
    rec = ((hist or {}).get("codes") or {}).get(code)
    if not rec or len(rec.get("s", [])) < 4:
        return None
    s = rec["s"]
    return round(s[-1] - s[-4], 1)


def build_screen(records, hist, kind="low_risk", limit=30):
    if kind not in KINDS:
        kind = "low_risk"
    title, lede, key, asc = KINDS[kind]
    inds = _industries()

    rows = []
    for code, r in records.items():
        if r.get("band") == "NO_DATA":
            continue
        v = _delta3(hist, code) if key == "delta3" else r.get(key)
        if v is None:
            continue
        rows.append((v, code, r))

    # 并列极多（最高分 86.5 有 26 只并列），主键排完顺序仍是任意的。
    # 必须给有意义的次级键，否则「榜单一二三名」只是字典序的产物。
    sec_key, sec_asc = _TIE_BREAK.get(kind, ("core_score", False))
    rows.sort(key=lambda x: x[1])
    rows.sort(key=lambda x: (x[2].get(sec_key) or 0), reverse=not sec_asc)
    rows.sort(key=lambda x: x[0], reverse=not asc)

    out = []
    for v, code, r in rows[:limit]:
        out.append({
            "code": code, "name": r.get("name", ""),
            "price": r.get("price"), "change_pct": r.get("change_pct"),
            "band": r.get("band"),
            "core_score": r.get("core_score"), "core_pctl": r.get("core_pctl"),
            "n_tied": r.get("n_tied"),
            "consensus_score": r.get("consensus_score"),
            "divergence": r.get("divergence"),
            "delta3": _delta3(hist, code),
            "sort_value": v,
            "badrate": r.get("badrate"),
            "flags": r.get("flags") or [],
            "soft_demote": r.get("soft_demote") or [],
            "core_imputed_books": r.get("core_imputed_books") or [],
            "pe_available": bool(r.get("pe_available", True)),
            "loss_maker": bool(r.get("loss_maker")),
            "industries": inds.get(code) or [],
        })

    meta = {
        "kind": kind, "title": title, "lede": lede,
        "n_universe": len(records), "n_returned": len(out),
        "industry_coverage_note": "行业标签仅覆盖约 35% 的股票（数据源限制）",
        "tiebreak_note": (
            f"核心分只有 199 个不同取值，并列极多（榜内常见并列 5~60 只）。"
            f"并列内按「{_TIE_LABEL.get(sec_key, sec_key)}」"
            f"{'升序' if sec_asc else '降序'}排列 —— 这只是可解释的排序，不是名次。"),
        "tiebreak_key": sec_key,
    }
    return meta, out


def kinds():
    return [{"kind": k, "title": v[0], "lede": v[1]} for k, v in KINDS.items()]


# ================================================================ 决策日志
# 复盘按**系统自己的承诺**打分，不按收益打分。
BAD_THRESH = -20.0      # 与 badrate.py 的「跌超 20%」口径一致
HORIZON = 60            # 60 个交易日


def _journal_path():
    return APP_DATA / JOURNAL_FILE


def _jload():
    try:
        return json.loads(_journal_path().read_text(encoding="utf-8"))
    except Exception:
        return []


def _jsave(rows):
    p = _journal_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def _kline(code):
    from .paths import CACHE_DIR
    p = CACHE_DIR / f"{code}.json"
    if not p.exists():
        return None
    try:
        return (json.loads(p.read_text(encoding="utf-8")) or {}).get("k") or None
    except Exception:
        return None


def verify_entry(entry):
    """按系统自己的口径复盘：入场后 60 个交易日内是否跌超 20%。

    用**最低价**而非收盘价衡量回撤 —— 更贴近真实经历。
    """
    k = _kline(entry["code"])
    if not k:
        return {"status": "no_data", "note": "K 线缺失"}
    dates = [r[0] for r in k]
    ed = entry["date"]

    # ⚠️ 基准价必须与复盘所用的价格序列**同源** —— 取 K 线里 <= 入场日的最后一根收盘。
    # 曾经直接用 entry.price_at_entry（来自快照），而窗口来自 K 线，两者错配：
    # 把日期回填到 2024 但基准价还是今天的，算出「最大回撤 +126.73%」这种不可能的值。
    # 生产里也会出问题：快照有几天延迟时，基准价会偏离实际入场价。
    j = None
    for idx, d in enumerate(dates):
        if d <= ed:
            j = idx
        else:
            break
    if j is None:
        return {"status": "pending", "progress": 0.0, "n_observed": 0,
                "note": "入场日早于数据起点"}
    base = k[j][4]
    if not base:
        return {"status": "no_data", "note": "入场日收盘价缺失"}

    window = k[j + 1:j + 1 + HORIZON]        # 入场日之后才开始算
    if not window:
        return {"status": "pending", "progress": 0.0, "n_observed": 0,
                "base_price": round(base, 3), "base_date": k[j][0]}
    lows = [r[3] for r in window]
    closes = [r[4] for r in window]
    min_low = min(lows)
    hit_date = next((r[0] for r in window if (r[3] / base - 1) * 100 <= BAD_THRESH), None)
    n = len(window)
    return {
        "status": "observed" if n >= HORIZON else "pending",
        "n_observed": n,
        "progress": round(min(n / HORIZON, 1.0) * 100, 1),
        "horizon_days": HORIZON,
        "base_price": round(base, 3),
        "base_date": k[j][0],           # 实际用作基准的那一天（可能早于 entry.date）
        "price_at_entry_recorded": entry.get("price_at_entry"),
        "min_low": round(min_low, 3),
        "max_drawdown_pct": round((min_low / base - 1) * 100, 2),
        "return_pct": round((closes[-1] / base - 1) * 100, 2),
        "last_date": window[-1][0],
        # ↓ 唯一的成败判据：系统自己承诺要避开的那个事件
        "hit_bad": bool(hit_date),
        "hit_date": hit_date,
    }


def journal_add(code, note, records, meta):
    r = (records or {}).get(code)
    if r is None:
        return None, "not_in_universe"
    entry = {
        "id": uuid.uuid4().hex[:10],
        "code": code, "name": r.get("name", ""),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "date": time.strftime("%Y-%m-%d"),
        # 入场时冻结判定与分数，事后不可改 —— 否则复盘会自欺
        "price_at_entry": r.get("price"),
        "band_at_entry": r.get("band"),
        "core_score_at_entry": r.get("core_score"),
        "core_pctl_at_entry": r.get("core_pctl"),
        "n_tied_at_entry": r.get("n_tied"),
        "consensus_at_entry": r.get("consensus_score"),
        "divergence_at_entry": r.get("divergence"),
        "expected_bad_rate": (r.get("badrate") or {}).get("bad_rate"),
        "base_bad_rate": (r.get("badrate") or {}).get("base_bad_rate"),
        "soft_demote": r.get("soft_demote") or [],
        "flags": r.get("flags") or [],
        "core_imputed_books": r.get("core_imputed_books") or [],
        "asof": (meta or {}).get("asof"),
        "note": note or "",
    }
    rows = _jload()
    rows.append(entry)
    _jsave(rows)
    return entry, None


def journal_remove(entry_id):
    rows = _jload()
    kept = [x for x in rows if x.get("id") != entry_id]
    if len(kept) == len(rows):
        return False
    _jsave(kept)
    return True


def journal_listing(records=None):
    rows = _jload()
    out = []
    for e in rows:
        v = verify_entry(e)
        cur = (records or {}).get(e["code"]) or {}
        band_now = cur.get("band")
        out.append({
            **e, "verify": v,
            "band_now": band_now,
            "core_score_now": cur.get("core_score"),
            "core_pctl_now": cur.get("core_pctl"),
            "band_changed": band_now is not None and band_now != e.get("band_at_entry"),
        })
    out.sort(key=lambda x: x["created_at"], reverse=True)

    done = [x for x in out if x["verify"].get("status") == "observed"]
    hits = [x for x in done if x["verify"].get("hit_bad")]
    summary = {
        "n_total": len(out),
        "n_observed": len(done),
        "n_pending": len(out) - len(done),
        "observed_bad_rate": round(len(hits) / len(done) * 100, 2) if done else None,
        "expected_bad_rate_mean": (
            round(sum(x["expected_bad_rate"] or 0 for x in done) / len(done), 2)
            if done else None),
        "base_bad_rate": (done[0]["base_bad_rate"] if done else None),
        "horizon_days": HORIZON,
        "bad_threshold_pct": BAD_THRESH,
        "note": (f"只按系统自己的承诺打分：入场后 {HORIZON} 个交易日内是否跌超 "
                 f"{abs(BAD_THRESH):.0f}%。不展示收益率作为成败判据 —— "
                 f"收益维度没有证据。"),
    }
    return out, summary
