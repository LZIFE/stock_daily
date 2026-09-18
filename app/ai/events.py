"""公告 / 研报抓取。

全部走东方财富公开接口，实测可用（2026-09-18）：
  - 公告列表   np-anotice-stock.eastmoney.com/api/security/ann
  - 公告正文   np-cnotice-stock.eastmoney.com/api/content/ann?art_code=
       ⚠️ 实测**5000 字符硬上限**：年报/半年报一律被截断，短公告(约1k)才完整。
       想看全文只能下 attach_list 里的 PDF —— 当前不做，在 data_limits 里声明。
  - 研报列表   reportapi.eastmoney.com/report/list
       ⚠️ 必须带 **qType=0**，否则 code 参数被忽略，返回全市场而非该股票。

实测覆盖率：公告充足（90 天 50+ 条，已超页大小）；
研报稀疏 —— 12 个随机样本中 8 个近半年为 0，含大盘股。
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import requests

from ..paths import EVENT_CACHE_DIR

UA = {"User-Agent": "Mozilla/5.0"}
ANN_LIST = "https://np-anotice-stock.eastmoney.com/api/security/ann"
ANN_TEXT = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
REPORT_LIST = "https://reportapi.eastmoney.com/report/list"

CACHE_TTL = 1800          # 30 分钟
ANNOUNCE_CHAR_LIMIT = 5000


def _cache_path(kind, code, day):
    return EVENT_CACHE_DIR / f"{code}_{kind}_{day}.json"


def _cache_get(p):
    try:
        if p.exists() and time.time() - p.stat().st_mtime < CACHE_TTL:
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _cache_put(p, data):
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _sym(code):
    return ("sh" if code[0] in "69" else "sz") + code


def fetch_announcements(code, limit=30):
    """返回 (items, error)。items: [{art_code, notice_date, title, columns}]"""
    day = time.strftime("%Y%m%d")
    cp = _cache_path("ann", code, day)
    cached = _cache_get(cp)
    if cached is not None:
        return cached["items"], cached.get("error")

    try:
        r = requests.get(ANN_LIST,
                         params={"sr": -1, "page_size": min(limit, 50), "page_index": 1,
                                 "ann_type": "A", "client_source": "web", "stock_list": code},
                         timeout=15, headers=UA)
        r.raise_for_status()
        lst = ((r.json().get("data") or {}).get("list") or [])
    except Exception as e:
        return [], f"{type(e).__name__}: {str(e)[:120]}"

    items = []
    for x in lst[:limit]:
        cols = x.get("columns") or []
        items.append({
            "art_code": x.get("art_code", ""),
            "notice_date": (x.get("notice_date") or "")[:10],
            "title": x.get("title", ""),
            "columns": [c.get("column_name") for c in cols if isinstance(c, dict)] or [],
        })
    _cache_put(cp, {"items": items, "error": None})
    return items, None


def fetch_announcement_text(art_code, limit=ANNOUNCE_CHAR_LIMIT):
    """单条公告正文。长公告会被截断到 5000 字符。"""
    try:
        r = requests.get(ANN_TEXT,
                         params={"art_code": art_code, "client_source": "web", "page_index": 1},
                         timeout=20, headers=UA)
        r.raise_for_status()
        body = ((r.json().get("data") or {}).get("notice_content") or "")
    except Exception:
        return ""
    return body[:limit]


def fetch_research_reports(code, days=180, limit=20):
    """返回 (items, rating_distribution, error)。

    ⚠️ qType=0 必须带，否则查出来是全市场。
    """
    day = time.strftime("%Y%m%d")
    cp = _cache_path("rep", code, day)
    cached = _cache_get(cp)
    if cached is not None:
        return cached["items"], cached.get("dist", {}), cached.get("error")

    end = time.strftime("%Y-%m-%d")
    begin = time.strftime("%Y-%m-%d", time.localtime(time.time() - days * 86400))
    try:
        r = requests.get(REPORT_LIST,
                         params={"industryCode": "*", "pageSize": min(limit, 50),
                                 "industry": "*", "rating": "*", "ratingChange": "*",
                                 "beginTime": begin, "endTime": end, "pageNo": 1,
                                 "fields": "", "qType": 0, "code": code},
                         timeout=15, headers=UA)
        r.raise_for_status()
        lst = r.json().get("data") or []
    except Exception as e:
        return [], {}, f"{type(e).__name__}: {str(e)[:120]}"

    items, dist = [], Counter()
    for x in lst[:limit]:
        rating = x.get("emRatingName") or ""
        if rating:
            dist[rating] += 1
        items.append({
            "publish_date": (x.get("publishDate") or "")[:10],
            "org": x.get("orgSName") or "",
            "title": x.get("title") or "",
            "rating": rating,
            "industry": x.get("industryName") or "",
        })
    _cache_put(cp, {"items": items, "dist": dict(dist), "error": None})
    return items, dict(dist), None


# ---- 「重要公告」筛选 ----
# 实测：90 天 50+ 条里关键词只命中 6–14 条（噪声 72–88%），
# 且纯关键词会漏掉「计提资产减值准备及资产报废」「监管问询函回复」「半年度报告」。
# 所以以 API 的 columns 分类为主，关键词为辅，两者取并集。
MATERIAL_COLUMNS = {
    "年报", "年度报告", "半年度报告全文", "半年度报告摘要", "季度报告", "业绩预告", "业绩快报",
    "对外担保", "提供/对外担保公告", "评级关注公告", "增持", "减持", "回购", "股权激励",
    "重大事项", "停牌", "退市", "诉讼", "关联交易", "问询", "监管", "资产重组", "募集",
}
MATERIAL_KEYWORDS = [
    "业绩", "年报", "半年报", "半年度报告", "季报", "一季度", "三季度",
    "减持", "增持", "诉讼", "问询", "监管", "关注", "重组", "分红", "回购",
    "停牌", "退市", "股权激励", "定增", "募资", "担保", "质押",
    "减值", "计提", "报废", "重大事项", "亏损", "预亏", "预增",
]


def pick_material(items, top=5):
    """挑出最重要的公告（供 AI 读正文）。

    排序：columns 命中 > 关键词命中 > 其余（按日期新到旧）。
    """
    scored = []
    for it in items:
        title = it.get("title", "")
        cols = set(it.get("columns") or [])
        s = 0
        if cols & MATERIAL_COLUMNS:
            s += 10
        if any(k in title for k in MATERIAL_KEYWORDS):
            s += 5
        scored.append((s, it.get("notice_date", ""), it))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [it for _, _, it in scored[:top]]
