"""决策日志 + 自动复盘。

把「信不信这套系统」变成可观测的问题：入场时冻结判定，事后按
**系统自己承诺的口径**（60 日内是否跌超 20%）自动验证。

不展示收益率作为成败判据 —— 收益维度没有证据。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import screen as S
from .. import snapshot
from ..schemas import JournalAddIn, JournalEntryOut, JournalOut

router = APIRouter()


@router.get("/journal", response_model=JournalOut)
def list_journal():
    try:
        records, meta, _ = snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})
    entries, summary = S.journal_listing(records)
    return JournalOut(entries=entries, summary=summary)


@router.post("/journal", response_model=JournalEntryOut)
def add_journal(body: JournalAddIn):
    try:
        records, meta, _ = snapshot.get()
    except snapshot.SnapshotNotReady as e:
        raise HTTPException(503, {"error": "snapshot_not_built", "hint": str(e)})

    code = snapshot.normalize(body.code)
    entry, err = S.journal_add(code, body.note, records, meta)
    if err == "not_in_universe":
        raise HTTPException(404, {"error": "not_in_universe",
                                  "hint": f"{code} 不在可算股票内"})
    entries, _ = S.journal_listing(records)
    for e in entries:
        if e["id"] == entry["id"]:
            return e
    return entry


@router.delete("/journal/{entry_id}")
def delete_journal(entry_id: str):
    if not S.journal_remove(entry_id):
        raise HTTPException(404, {"error": "entry_not_found"})
    return {"ok": True, "id": entry_id}
