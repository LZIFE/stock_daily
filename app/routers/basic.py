"""健康检查 / 快照元数据 / 股票搜索 / 核心分直方图。"""
from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Query

from .. import disclaimers, snapshot
from ..ai.client import probe
from ..schemas import (EvidenceOut, HealthOut, SnapshotMetaOut,
                       StockSearchOut)

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health():
    try:
        records, meta, bt = snapshot.get()
        ready = True
        asof = meta.get("asof")
        n = meta.get("n_scored")
        hint = None
    except snapshot.SnapshotNotReady as e:
        ready, asof, n = False, None, None
        hint = str(e)
        bt = {}

    ai_ok, ai_model = probe()
    return HealthOut(
        status="ok" if ready else "snapshot_missing",
        snapshot_ready=ready, asof=asof, universe_size=n,
        scorer_sha256=(bt.get("meta") or {}).get("scorer_sha256"),
        panel_sha256=(bt.get("meta") or {}).get("panel_sha256"),
        ai_available=bool(ai_ok), ai_model=ai_model or None,
        version="0.1.0", hint=hint,
    )


@router.get("/snapshot/meta", response_model=SnapshotMetaOut)
def snapshot_meta():
    try:
        records, meta, bt = snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})

    ev = None
    if bt and "oos" in bt:
        o = bt["oos"]
        ev = EvidenceOut(window="oos", n=o.get("n", 0),
                         base_bad_rate=o.get("base_bad_rate", 0.0),
                         auc=o.get("auc", 0.0),
                         quintiles=o.get("quintiles", []),
                         quintile_edges=o.get("quintile_edges", []))
    return SnapshotMetaOut(**{k: meta.get(k) for k in
                              ("asof", "built_at", "universe_size", "n_scored",
                               "band_distribution", "coverage", "core_score", "core_books")},
                           evidence=ev, disclaimers=disclaimers.BASE)


@router.get("/stocks/search", response_model=StockSearchOut)
def stocks_search(q: str = Query("", min_length=1), limit: int = Query(10, ge=1, le=50)):
    try:
        snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})
    return StockSearchOut(q=q, items=snapshot.search(q, limit))


@router.get("/universe/histogram")
def universe_histogram(bins: int = Query(40, ge=10, le=100)):
    try:
        snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})
    return snapshot.histogram(bins)
