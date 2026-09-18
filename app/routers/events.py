"""公告 / 研报（确定性端点，与 AI 无关）。

放在事实层：这些是抓到的原始材料，不是模型的解读。
前端应独立展示，让用户在读 AI 解读前先看到原始公告。
"""
from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Query

from .. import snapshot
from ..ai.events import fetch_announcements, fetch_research_reports
from ..schemas import (AnnouncementItem, AnnouncementListOut,
                       ResearchReportItem, ResearchReportListOut)

router = APIRouter()


def _known(code):
    try:
        rec, meta = snapshot.get_record(code)
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})
    if rec is None:
        raise HTTPException(404, {"error": "not_in_universe"})
    return rec


@router.get("/announcements/{code}", response_model=AnnouncementListOut)
def announcements(code: str, limit: int = Query(30, ge=1, le=50)):
    _known(code)
    items, err = fetch_announcements(code, limit)
    return AnnouncementListOut(
        code=code, items=[AnnouncementItem(**x) for x in items],
        fetched_at=time.strftime("%Y-%m-%d %H:%M:%S"), error=err)


@router.get("/research-reports/{code}", response_model=ResearchReportListOut)
def research_reports(code: str, days: int = Query(180, ge=30, le=730),
                     limit: int = Query(20, ge=1, le=50)):
    _known(code)
    items, dist, err = fetch_research_reports(code, days, limit)
    note = None
    if not err and not items:
        note = "近半年无券商覆盖（实测约 2/3 的股票研报数为 0，含部分大盘股）"
    return ResearchReportListOut(
        code=code, items=[ResearchReportItem(**x) for x in items],
        rating_distribution=dist, fetched_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        error=err, note=note)
