"""快照加载与查询。

运行时**只查表**，不重算 —— 单只股票单独算不出横截面分位，这是硬约束。

设计原则：**fail closed**。
快照不存在时宁可返回 503 让前端显示引导页，也绝不在请求里现算
（一次全市场构建 2.6 分钟，塞进请求里是灾难）。
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from .paths import SNAPSHOT_DIR


class SnapshotNotReady(Exception):
    pass


_CACHE: dict = {"dir": None, "records": None, "meta": None, "badrate": None, "index": None}


def available_dirs():
    if not SNAPSHOT_DIR.is_dir():
        return []
    return sorted([p for p in SNAPSHOT_DIR.iterdir()
                   if p.is_dir() and not p.name.startswith("_")],
                  key=lambda p: p.name, reverse=True)


def load(dir_path=None, force=False):
    """加载快照（默认最新一份）。返回 (records, meta, badrate)。"""
    if dir_path is None:
        dirs = available_dirs()
        if not dirs:
            raise SnapshotNotReady(
                f"没有找到快照。请先运行：python -m app.build_snapshot")
        dir_path = dirs[0]
    dir_path = Path(dir_path)

    if not force and _CACHE["dir"] == dir_path and _CACHE["records"] is not None:
        return _CACHE["records"], _CACHE["meta"], _CACHE["badrate"]

    scores = dir_path / "scores.jsonl.gz"
    if not scores.exists():
        raise SnapshotNotReady(f"快照不完整：{scores} 不存在")

    records = {}
    with gzip.open(scores, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            records[r["code"]] = r

    meta = {}
    mp = dir_path / "snapshot_meta.json"
    if mp.exists():
        meta = json.loads(mp.read_text(encoding="utf-8"))

    badrate = {}
    bp = dir_path / "badrate_table.json"
    if bp.exists():
        badrate = json.loads(bp.read_text(encoding="utf-8"))

    index = [(r["code"], r.get("name", "")) for r in records.values()]

    _CACHE.update({"dir": dir_path, "records": records, "meta": meta,
                   "badrate": badrate, "index": index,
                   "cluster_stats": _cluster_stats(records),
                   "history": None})
    return records, meta, badrate


def _cluster_stats(records):
    """各语义簇的全市场基准（中位/四分位）。

    在服务端启动时从快照现算，**不写进快照文件** —— 这样加这个功能
    不需要重建快照（重建一次 2.5 分钟）。4898 × 29 只算一次，很便宜。
    """
    from . import book_rules
    out = {}
    for c, books in book_rules.cluster_members().items():
        vals = []
        for r in records.values():
            s = [r["books"].get(b) for b in books]
            s = [x for x in s if x is not None]
            if s:
                vals.append(sum(s) / len(s))
        if not vals:
            continue
        vals.sort()
        n = len(vals)
        out[c] = {
            "cluster": c, "label": book_rules.cluster_label(c),
            "n_books": len(books), "books": books,
            "median": round(vals[n // 2], 1),
            "p25": round(vals[int(0.25 * n)], 1),
            "p75": round(vals[int(0.75 * n)], 1),
            "n_stocks": n,
        }
    return out


def cluster_stats():
    if _CACHE.get("cluster_stats") is None:
        load()
    return _CACHE.get("cluster_stats") or {}


def history():
    """历史轨迹（来自 bt_robust_data.pkl，构建期写入快照目录）。"""
    if _CACHE.get("history") is None and _CACHE.get("dir"):
        from . import history as H
        _CACHE["history"] = H.load(_CACHE["dir"]) or {}
    return _CACHE.get("history") or {}


def get():
    """对外入口。快照未就绪时抛 SnapshotNotReady。"""
    return load()


def normalize(code):
    code = (code or "").strip().lower()
    for pre in ("sh", "sz", "bj"):
        if code.startswith(pre):
            code = code[len(pre):]
    return code.zfill(6) if code.isdigit() else code


def get_record(code):
    records, meta, _ = load()
    c = normalize(code)
    if c not in records:
        return None, meta
    return records[c], meta


def search(q, limit=10):
    if _CACHE["index"] is None:
        load()
    q = (q or "").strip()
    if not q:
        return []
    ql = q.lower()
    hits = []
    for code, name in _CACHE["index"]:
        if code.startswith(ql):
            hits.append((0, code, name))
        elif ql in code:
            hits.append((1, code, name))
        elif ql in (name or "").lower():
            hits.append((2, code, name))
        if len(hits) > limit * 20:
            break
    hits.sort(key=lambda x: (x[0], x[1]))
    out = []
    records = _CACHE["records"] or {}
    for _, code, name in hits[:limit]:
        r = records.get(code, {})
        out.append({"code": code, "name": name,
                    "price": r.get("price"), "band": r.get("band"),
                    "core_score": r.get("core_score"), "core_pctl": r.get("core_pctl")})
    return out


def histogram(bins=40):
    records = _CACHE["records"] or load()[0]
    vals = sorted(r["core_score"] for r in records.values())
    if not vals:
        return {"edges": [], "counts": []}
    lo, hi = vals[0], vals[-1]
    step = max((hi - lo) / bins, 0.5)
    edges, counts = [], []
    for i in range(bins):
        e = lo + step * i
        edges.append(round(e, 2))
        counts.append(sum(1 for v in vals if e <= v < e + step))
    return {"edges": edges, "counts": counts,
            "core_min": lo, "core_median": vals[len(vals) // 2], "core_max": hi}
