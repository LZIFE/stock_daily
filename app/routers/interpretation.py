"""AI 解读端点。

**这个端点慢**（实测 12–60s），前端必须异步调用 + 骨架屏，
不能让它阻塞判定卡的渲染 —— 判定卡走 /api/analysis，是毫秒级的。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import snapshot
from ..ai import interpreter

router = APIRouter()


class InterpretRequest(BaseModel):
    force_refresh: bool = False
    include_events: bool = True


@router.post("/interpretation/{code}")
def interpretation(code: str, body: InterpretRequest = InterpretRequest()):
    try:
        snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})

    out = interpreter.interpret(code, force=body.force_refresh,
                                include_events=body.include_events)
    if out is None:
        raise HTTPException(404, {"error": "not_in_universe"})
    return out
