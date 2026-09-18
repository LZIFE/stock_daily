"""AI 解读编排：抓事件 → 构造提示 → 调 LLM → 修复 → 过护栏 → 缓存。

**任何一步失败都必须降级，而不是编造。**
- LLM 不可用       → degraded，sections=None，确定性报告不受影响
- 事件抓取失败      → event_scan 为空 + warning，绝不编造事件
- JSON 修不好       → degraded
- 判定被模型改写    → 服务端强制覆盖（engine 永远赢）
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .. import book_rules, disclaimers, snapshot
from ..paths import AI_CACHE_DIR
from . import client, events as ev, guard, prompt

CACHE_TTL = 24 * 3600
ANNOUNCE_TEXT_BUDGET = 6000        # 全部正文合计硬上限
PROMPT_VERSION = prompt.PROMPT_VERSION


def _cache_file(code, asof, model):
    slug = (model or "none").replace("/", "_")
    return AI_CACHE_DIR / f"{code}_{asof}_{slug}_{PROMPT_VERSION}.json"


def _hash(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()[:16]


def _gather_events(code, include=True):
    """返回 (events, limits, warnings)。"""
    if not include:
        return None, ["本次未请求公告/研报"], []
    limits, warn = [], []
    items, err = ev.fetch_announcements(code, 30)
    if err:
        warn.append(f"公告抓取失败：{err}")
    material = ev.pick_material(items, 5)
    used = 0
    for a in material:
        if used >= ANNOUNCE_TEXT_BUDGET:
            a["body"] = ""
            continue
        body = ev.fetch_announcement_text(a["art_code"])
        if len(body) >= ev.ANNOUNCE_CHAR_LIMIT:
            # 实测（贵州茅台 2026 半年报）：营收/归母净利/经营现金流/归母净资产/
            # 总资产/EPS/加权 ROE 全部落在前 4000 字内，被截掉的是「非经常性损益」
            # 等附录细节。所以这个上限**不是有效信息的瓶颈** —— 措辞按实测来，
            # 不要写成吓人的样子（也就不必为此引入 PDF 解析依赖）。
            limits.append("公告正文接口上限 5000 字符；实测关键财务数据均在正文前 4000 字内，"
                          "截断的是非经常性损益等附录细节")
        take = min(len(body), ANNOUNCE_TEXT_BUDGET - used)
        a["body"] = body[:take]
        used += take

    reps, dist, rerr = ev.fetch_research_reports(code, 180, 20)
    if rerr:
        warn.append(f"研报抓取失败：{rerr}")
    if not rerr and not reps:
        limits.append("近半年无券商覆盖")
    return ({"announcements": material, "reports": reps, "rating_distribution": dist},
            limits, warn)


def interpret(code: str, force: bool = False, include_events: bool = True):
    """返回 InterpretationOut 所需的 dict。"""
    rec, meta = snapshot.get_record(code)
    if rec is None:
        return None
    asof = meta.get("asof")
    model = None
    c, model = client.resolve()
    out = {
        "code": rec["code"], "asof": asof, "cached": False,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": model, "prompt_version": PROMPT_VERSION,
        "degraded": True, "warnings": [], "sections": None, "sources": [],
        "disclaimers": disclaimers.for_record(rec, include_ai=True),
    }

    evs, limits, warn = _gather_events(code, include_events)
    out["warnings"] += warn

    payload_hash = _hash({"rec": {k: rec.get(k) for k in
                                  ("core_score", "core_pctl", "band", "consensus_score",
                                   "divergence", "books", "book_available", "tech", "fin",
                                   "pct", "badrate", "core_imputed_books")},
                          "events": evs, "limits": limits})
    out["payload_hash"] = payload_hash

    cf = _cache_file(rec["code"], asof, model)
    if not force and cf.exists():
        try:
            cached = json.loads(cf.read_text(encoding="utf-8"))
            if (cached.get("payload_hash") == payload_hash
                    and time.time() - cf.stat().st_mtime < CACHE_TTL):
                cached["cached"] = True
                return cached
        except Exception:
            pass

    if not c:
        out["warnings"].append("AI 不可用（未配置或探测失败）；本次仅返回规则层结果。")
        return out

    user = prompt.build_user(rec, meta, evs, limits)
    text, model_used = client.complete(prompt.SYSTEM, user, max_tokens=2500)
    out["model"] = model_used or model

    if not text:
        out["warnings"].append("模型调用失败（超时或错误）。")
        return out

    parsed, how = guard.repair_json(text)
    if parsed is None:
        out["warnings"].append(f"模型输出无法解析为 JSON（{how}）。")
        return out
    if how != "clean":
        out["warnings"].append(f"模型输出格式不合规，已修复（{how}）。")

    parsed, w, _ = guard.guard(parsed, rec.get("band"), book_rules.CORE_BOOKS,
                               rec.get("core_score"), rec.get("core_pctl"))
    out["warnings"] += w

    out["sections"] = parsed
    out["degraded"] = False
    out["sources"] = [{"kind": "announcement", "title": a.get("title", ""),
                       "date": a.get("notice_date", "")}
                      for a in (evs or {}).get("announcements", [])] + \
                     [{"kind": "report", "title": r.get("title", ""),
                       "date": r.get("publish_date", ""), "org": r.get("org", "")}
                      for r in (evs or {}).get("reports", [])]

    try:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return out
