"""API 数据契约（Pydantic）。

前端的 TS 类型可以从 /docs 的 OpenAPI 直接生成，所以这里就是前后端的唯一约定。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from . import book_rules


class HealthOut(BaseModel):
    status: str
    snapshot_ready: bool
    asof: Optional[str] = None
    universe_size: Optional[int] = None
    scorer_sha256: Optional[str] = None
    panel_sha256: Optional[str] = None
    ai_available: bool = False
    ai_model: Optional[str] = None
    version: str = ""
    hint: Optional[str] = None


class EvidenceOut(BaseModel):
    window: str = "oos"
    n: int = 0
    base_bad_rate: float = 0.0
    auc: float = 0.0
    quintiles: List[float] = Field(default_factory=list)
    quintile_edges: List[float] = Field(default_factory=list)


class SnapshotMetaOut(BaseModel):
    asof: Optional[str] = None
    built_at: Optional[str] = None
    universe_size: Optional[int] = None
    n_scored: Optional[int] = None
    band_distribution: Dict[str, int] = Field(default_factory=dict)
    coverage: Dict[str, Any] = Field(default_factory=dict)
    core_score: Dict[str, Any] = Field(default_factory=dict)
    core_books: List[str] = Field(default_factory=lambda: list(book_rules.CORE_BOOKS))
    evidence: Optional[EvidenceOut] = None
    disclaimers: List[str] = Field(default_factory=list)


class StockSearchItem(BaseModel):
    code: str
    name: str = ""
    price: Optional[float] = None
    band: Optional[str] = None
    core_score: Optional[float] = None
    core_pctl: Optional[float] = None


class StockSearchOut(BaseModel):
    q: str
    items: List[StockSearchItem] = Field(default_factory=list)


class BookScoreOut(BaseModel):
    name: str
    score: Optional[float] = None          # None = 算不出来，绝不是 50
    available: bool = True
    core: bool = False
    cluster: str = ""
    rule: str = ""


class AnalysisOut(BaseModel):
    code: str
    name: str = ""
    asof: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    band: Optional[str] = None
    core_score: Optional[float] = None
    core_pctl: Optional[float] = None
    n_tied: Optional[int] = None
    consensus_score: Optional[float] = None
    divergence: Optional[float] = None
    coverage_pct: Optional[float] = None
    core_coverage_pct: Optional[float] = None
    pe_available: bool = True
    loss_maker: bool = False
    quality_bad: bool = False
    # 核心分里有几本依赖兜底值（不可算但仍参与计算，见 scoring.finalize 注释）
    core_imputed_books: List[str] = Field(default_factory=list)
    n_books_available: Optional[int] = None
    n_books_total: Optional[int] = None
    soft_demote: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    position_cap_pct: Optional[float] = None
    tech: Dict[str, Any] = Field(default_factory=dict)
    fin: Dict[str, Any] = Field(default_factory=dict)
    pct: Dict[str, Any] = Field(default_factory=dict)
    period: Dict[str, Any] = Field(default_factory=dict)
    books: List[BookScoreOut] = Field(default_factory=list)
    badrate: Optional[Dict[str, Any]] = None
    disclaimers: List[str] = Field(default_factory=list)


class AnnouncementItem(BaseModel):
    art_code: str = ""
    notice_date: str = ""
    title: str = ""
    columns: List[str] = Field(default_factory=list)


class AnnouncementListOut(BaseModel):
    code: str
    items: List[AnnouncementItem] = Field(default_factory=list)
    fetched_at: Optional[str] = None
    error: Optional[str] = None


class ResearchReportItem(BaseModel):
    publish_date: str = ""
    org: str = ""
    title: str = ""
    rating: str = ""
    industry: str = ""


class ResearchReportListOut(BaseModel):
    code: str
    items: List[ResearchReportItem] = Field(default_factory=list)
    rating_distribution: Dict[str, int] = Field(default_factory=dict)
    fetched_at: Optional[str] = None
    error: Optional[str] = None
    note: Optional[str] = None


class ErrorOut(BaseModel):
    error: str
    hint: Optional[str] = None
