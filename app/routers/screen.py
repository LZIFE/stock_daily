"""全市场榜单。

命名与呈现的诚实性（决定用户怎么用它，不是文案问题）：
  · 叫「低踩雷概率」而不是「推荐买入」
  · 每条带并列只数与该桶历史坏率
  · 明确写出「这不是收益策略」
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import screen as S
from .. import snapshot
from ..schemas import ScreenKindOut, ScreenMetaOut, ScreenOut

router = APIRouter()


@router.get("/screen/kinds", response_model=list[ScreenKindOut])
def kinds():
    return S.kinds()


@router.get("/screen", response_model=ScreenOut)
def screen(
    kind: str = Query("low_risk"),
    limit: int = Query(30, ge=5, le=100),
):
    try:
        records, meta, _ = snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})

    m, rows = S.build_screen(records, snapshot.history(), kind, limit)
    return ScreenOut(meta=ScreenMetaOut(**m), rows=rows, disclaimer=S.DISCLAIMER)
