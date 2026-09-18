"""算分适配器：把一只股票的缓存文件转成完整评分记录。

**本模块不实现任何规则。** 规则只在根目录 bt_scorer.py 里；
这里只负责正确地把数据喂进去、并把结果标注清楚。

三个必须遵守的 parity 细节（错一个，全部数字就与回测对不上）：
 1. 窗口取 `k[i-129 : i+1]`（130 根收盘），i 为 ASOF 在 k 中的下标。
 2. `books9_new(t, f, price, pct_vol, pct_turn)` 的 **pct_turn 传的是 amt20 横截面分位**，
    不是换手率分位 —— 与 bt_prep_robust.py:129-130 保持一致。
 3. `derived_fin` 返回 None 时转空 dict，**不要**改成别的行为（回测就是这么跑的）。

关于「算不出来」：
    bt_scorer 在输入缺失时回退 50，无法从返回值区分「算出来 50」和「算不出来」。
    所以本模块用 book_rules 的依赖字段判定 available，
    **不可用时把分数置 None**，绝不让 50 冒充真实分数。
"""
from __future__ import annotations

from . import book_rules
from .paths import ensure_scorer_importable

ensure_scorer_importable()          # 必须在 import bt_scorer 之前
from bt_scorer import (  # noqa: E402
    ALL29, books20, books9_new, derived_fin, percentile_rank, tech,
)

CORE_BOOKS = book_rules.CORE_BOOKS
CONSENSUS_BOOKS = book_rules.CONSENSUS_BOOKS

# 覆盖率口径：与根目录 score_v2.py 一致，便于交叉校验
TECH_FIELDS = ["ma5", "ma20", "ma60", "pos60", "dd60", "vol_ratio", "up5", "up20", "up60",
               "yang5", "amp60", "dif", "volat", "ma20_slope"]
FIN_FIELDS = ["pe", "pb", "roe", "gm", "debt", "np_yoy", "rev_yoy", "ocf_ttm", "np_ttm", "eps_ttm"]

MIN_KLINE = 200
WINDOW = 130


# ------------------------------------------------------------------ Pass 1
def build_intermediate(code, k, fin, asof):
    """解析 + tech + PIT 财务 + 旧 20 本。

    返回 None 表示这只股票不可算（由调用方记跳过原因）。
    新 9 本要等 Pass 2 拿到横截面分位才能算。
    """
    if not isinstance(k, list) or len(k) < MIN_KLINE or not isinstance(fin, list) or not fin:
        return None
    idx = {row[0]: i for i, row in enumerate(k)}.get(asof)
    if idx is None or idx < WINDOW - 1:
        return None
    win = k[idx - WINDOW + 1: idx + 1]

    try:
        t = tech(win)
    except Exception:
        return None

    closes = [r[4] for r in win]
    prev = closes[-2]
    chg = (closes[-1] / prev - 1) * 100 if prev else 0.0
    amt20 = sum(k[j][5] * k[j][4] for j in range(idx - 19, idx + 1)) / 20.0

    visible = [x for x in fin if x.get("nd") and x["nd"] <= asof]
    f = derived_fin(visible, asof, t["close"]) or {}

    try:
        b20 = books20(t, f, t["close"], chg, amt20)
    except Exception:
        return None

    last = visible[-1] if visible else {}
    return {
        "code": code, "t": t, "f": f, "price": t["close"],
        "chg": chg, "amt20": amt20, "b20": b20,
        "period": {"rd": last.get("rd"), "nd": last.get("nd")},
    }


# ------------------------------------------------------------------ Pass 2
def compute_books(t, f, price, chg, amt20, pct_vol, pct_turn):
    """29 本分数（顺序与 ALL29 一致）。"""
    out = {}
    out.update(books20(t, f, price, chg, amt20))
    out.update(books9_new(t, f, price, pct_vol, pct_turn))
    return {name: out.get(name) for name in ALL29}


def _field_value(name, t, f, amount=None, pct=None):
    if name in ("amount",):
        return amount
    if pct and name in pct:
        return pct[name]
    if name in t:
        return t.get(name)
    if name in f:
        return f.get(name)
    return None


def coverage(t, f, amount=None, pct=None):
    """整体覆盖率 + 缺失字段。"""
    missing = []
    for name in TECH_FIELDS:
        if t.get(name) is None:
            missing.append(name)
    for name in FIN_FIELDS:
        if f.get(name) is None:
            missing.append(name)
    total = len(TECH_FIELDS) + len(FIN_FIELDS)
    return round((total - len(missing)) / total * 100, 1), missing


def core_coverage(t, f, amount=None, pct=None):
    """核心 4 本的字段覆盖率 —— 决定能不能出判定。"""
    need = []
    for bk in CORE_BOOKS:
        m = book_rules.BOOKS.get(bk, {})
        for name in list(m.get("tech", [])) + list(m.get("fin", [])) + list(m.get("xsec", [])):
            if name not in need:
                need.append(name)
    missing = [n for n in need if _field_value(n, t, f, amount, pct) is None]
    if not need:
        return 100.0, []
    return round((len(need) - len(missing)) / len(need) * 100, 1), missing


_RANK = {"AVOID": 0, "WATCH": 1, "BUY": 2}


def band(core_pctl, soft_demote, hard_veto, core_cov, min_cov, buy_pctl, watch_pctl):
    """三态判定。

    顺序：hard_veto > 覆盖率不足 > 按分位定档 > soft_demote **封顶**。

    ⚠️ 曾经写成 `if soft_demote: return "WATCH"` —— 那是「至少 WATCH」，
    会把 AVOID **提升**成 WATCH。实测后果：核心分 27.0、分位 0.0（全市场最低）
    的股票因为「交易拥挤」被显示成 WATCH。
    **降级必须封顶，不能抬底。** 语义上「估值极端 / 拥挤」只会降低吸引力。

    注意：**没有绝对分数阈值**。v1 的 75/60 是拍脑袋定的，
    分档只能靠全市场分位标定（config 的 buy_pctl=90 / watch_pctl=70）。
    """
    if hard_veto:
        return "EXCLUDED"
    if core_cov < min_cov:
        return "NO_DATA"

    base = "BUY" if core_pctl >= buy_pctl else ("WATCH" if core_pctl >= watch_pctl else "AVOID")
    if soft_demote and _RANK[base] > _RANK["WATCH"]:
        return "WATCH"           # 只封顶，不抬底
    return base


def availability(books, t, f, amount=None, pct=None):
    """逐本判定是否真能算。依赖字段缺一个 → 不可用（分数置 None）。"""
    out = {}
    for name in ALL29:
        m = book_rules.BOOKS.get(name, {})
        ok = True
        for fld in list(m.get("tech", [])) + list(m.get("fin", [])) + list(m.get("xsec", [])):
            if _field_value(fld, t, f, amount, pct) is None:
                ok = False
                break
        out[name] = bool(ok)
    return out


def finalize(rec, xsec, amount=None):
    """补齐横截面分位 → 算新 9 本 → 核心分/共识分/分歧 → 门禁标注。"""
    t, f = rec["t"], rec["f"]
    pct = {
        "vol": percentile_rank(xsec["vols"], t["volat"]) if xsec.get("vols") and t.get("volat") else 50.0,
        "amt": percentile_rank(xsec["ams"], rec["amt20"]) if xsec.get("ams") else 50.0,
    }
    pct["pe"] = percentile_rank(xsec["pes"], f["pe"]) if xsec.get("pes") and f.get("pe") and f["pe"] > 0 else None
    pct["pb"] = percentile_rank(xsec["pbs"], f["pb"]) if xsec.get("pbs") and f.get("pb") and f["pb"] > 0 else None

    amt = rec["amt20"]
    books = compute_books(t, f, rec["price"], rec["chg"], amt, pct["vol"], pct["amt"])
    avail = availability(books, t, f, amount=amt, pct=pct)
    # 不可用 → 分数置 None，绝不显示成 50
    shown = {k: (v if avail.get(k) else None) for k, v in books.items()}

    # 核心分**必须**用含兜底值的原始分数算 —— 回测验证的就是这个版本
    # （bt_scorer 在输入缺失时回退 50，回测面板里也是这样）。
    # 改成「只按可用的书求均值」会破坏 parity，等于丢掉整套证据链。
    #
    # 但兜底不能藏着：把这些书单独列出来，UI 必须说明
    # 「核心分里有 N/4 本依赖兜底值」。
    core = sum(books[b] for b in CORE_BOOKS) / len(CORE_BOOKS)
    cons = sum(books[b] for b in CONSENSUS_BOOKS) / len(CONSENSUS_BOOKS)
    core_imputed = [b for b in CORE_BOOKS if not avail.get(b)]
    cons_imputed = [b for b in CONSENSUS_BOOKS if not avail.get(b)]

    cov, miss = coverage(t, f, amount=amt, pct=pct)
    ccov, cmiss = core_coverage(t, f, amount=amt, pct=pct)

    # ---- L0 门禁：只标注/降级，流动性不否决（实证 lift 0.63 显著反向）----
    soft, hard, flags = [], [], []
    if (pct["pe"] is not None and pct["pe"] > 95) or (pct["pb"] is not None and pct["pb"] > 95):
        soft.append("估值极端")
    if pct["amt"] is not None and pct["amt"] > 90:
        soft.append("交易拥挤")
    # 财务可信门：缓存里没有「连续 N 年」的年报序列，规则未实现，不得假装实现
    if amt is not None and amt < 5e7:
        flags.append("流动性受限")

    return {
        "code": rec["code"], "price": rec["price"], "change_pct": round(rec["chg"], 2),
        "amt20": amt,
        "tech": {k: t.get(k) for k in TECH_FIELDS + ["close"]},
        "fin": {k: f.get(k) for k in FIN_FIELDS},
        "period": rec["period"],
        "pct": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in pct.items()},
        "coverage_pct": cov, "missing_fields": miss,
        "core_coverage_pct": ccov, "core_missing_fields": cmiss,
        "quality_bad": bool(f.get("quality_bad")),
        "pe_available": f.get("pe") is not None,
        "loss_maker": bool(f.get("eps_ttm") is not None and f["eps_ttm"] <= 0),
        "books": shown, "book_available": avail,
        "core_score": round(core, 2), "consensus_score": round(cons, 2),
        "divergence": round(core - cons, 2),
        "core_imputed_books": core_imputed,
        "n_books_available": sum(1 for v in avail.values() if v),
        "n_books_total": len(avail),
        "soft_demote": soft, "hard_veto": hard, "flags": flags,
    }
