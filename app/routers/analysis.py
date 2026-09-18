"""单只股票的完整分析。

返回的 29 本书里，算不出来的分数是 **null**，不是 50 ——
「算不出来」不能冒充「中性」，这是对抗性审查 A1 的硬要求。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import book_rules, disclaimers, history as hist_mod, snapshot
from ..schemas import AnalysisOut, BookScoreOut, ClusterScoreOut, HistoryOut

router = APIRouter()


def _clusters(rec):
    """把 29 本归到语义簇 —— 29 个数字读不了，9 个簇能读。"""
    stats = snapshot.cluster_stats()
    out = []
    for c, members in book_rules.cluster_members().items():
        vals = [rec["books"].get(b) for b in members]
        vals = [v for v in vals if v is not None]
        st = stats.get(c) or {}
        score = round(sum(vals) / len(vals), 1) if vals else None
        med = st.get("median")
        out.append(ClusterScoreOut(
            cluster=c, label=book_rules.cluster_label(c),
            desc=book_rules.cluster_desc(c),
            score=score, universe_median=med,
            diff=(round(score - med, 1) if score is not None and med is not None else None),
            n_books=len(members), n_available=len(vals), books=members,
            has_core=any(b in book_rules.CORE_BOOKS for b in members)))
    return out


def _history(rec, meta):
    h = snapshot.history()
    s = hist_mod.series(h, rec["code"],
                        (meta.get("asof"), rec.get("core_score"), rec.get("core_pctl")))
    return HistoryOut(**s) if s else None


def _to_out(rec, meta):
    books = []
    for name in book_rules.ORDER:
        m = book_rules.BOOKS.get(name, {})
        books.append(BookScoreOut(
            name=name,
            score=rec["books"].get(name),
            available=bool(rec["book_available"].get(name)),
            core=name in book_rules.CORE_BOOKS,
            cluster=m.get("cluster", ""),
            rule=m.get("rule", ""),
        ))
    return AnalysisOut(
        code=rec["code"], name=rec.get("name", ""), asof=meta.get("asof"),
        price=rec.get("price"), change_pct=rec.get("change_pct"),
        band=rec.get("band"),
        core_score=rec.get("core_score"), core_pctl=rec.get("core_pctl"),
        n_tied=rec.get("n_tied"),
        consensus_score=rec.get("consensus_score"), divergence=rec.get("divergence"),
        coverage_pct=rec.get("coverage_pct"), core_coverage_pct=rec.get("core_coverage_pct"),
        pe_available=bool(rec.get("pe_available", True)),
        loss_maker=bool(rec.get("loss_maker")),
        quality_bad=bool(rec.get("quality_bad")),
        core_imputed_books=rec.get("core_imputed_books") or [],
        n_books_available=rec.get("n_books_available"),
        n_books_total=rec.get("n_books_total"),
        soft_demote=rec.get("soft_demote") or [], flags=rec.get("flags") or [],
        position_cap_pct=rec.get("position_cap_pct"),
        tech=rec.get("tech") or {}, fin=rec.get("fin") or {},
        pct=rec.get("pct") or {}, period=rec.get("period") or {},
        books=books, clusters=_clusters(rec), history=_history(rec, meta),
        badrate=rec.get("badrate"),
        disclaimers=disclaimers.for_record(rec),
    )


@router.get("/analysis/{code}", response_model=AnalysisOut)
def analysis(code: str):
    try:
        rec, meta = snapshot.get_record(code)
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})
    if rec is None:
        raise HTTPException(404, {"error": "not_in_universe",
                                  "hint": f"{code} 不在 {meta.get('n_scored', 0)} 只可算股票内"})
    return _to_out(rec, meta)
