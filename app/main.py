"""FastAPI 应用入口。

启动：
    uvicorn app.main:app --reload --port 8000
文档：
    http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__, snapshot
from .routers import analysis, basic, events, interpretation, journal, screen

app = FastAPI(
    title="29 本书观点 · 个股买入决策",
    version=__version__,
    description="输入 A 股代码，返回 29 本投资书的逐本观点与判定。"
                "判定由确定性规则引擎给出；AI 只做解读，不得修改判定。",
)

# 开发期：Vite dev server 在 5173，需要跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "*"],
    allow_methods=["GET", "POST"], allow_headers=["*"],
)


@app.exception_handler(snapshot.SnapshotNotReady)
async def _snapshot_not_ready(request: Request, exc: Exception):
    return JSONResponse(status_code=503, content={
        "error": "snapshot_not_built",
        "hint": "python -m app.build_snapshot",
        "detail": str(exc),
    })


app.include_router(basic.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(interpretation.router, prefix="/api")
app.include_router(screen.router, prefix="/api")
app.include_router(journal.router, prefix="/api")


@app.get("/api/ping")
def ping():
    return {"ok": True, "version": __version__}


# 前端构建产物（阶段 4 之后才有）。有则托管，没有就只提供 API。
_dist = Path(__file__).resolve().parents[1] / "web" / "dist"
if _dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="web")
