"""分桶历史坏率 —— 从回测面板算，绝不硬编码。

文档里流传的数字（18.34%→5.62% 等）是 dd60 修复**之前**的，与当前面板不一致。
所以所有对外展示的证据数字都在构建时从盘上算出来，并记录 panel / scorer 的 SHA-256，
让「展示的证据」与「产生它的代码版本」绑定。

口径：
    核心分 = 4 本核心书等权均值
    坏结果 = 未来 60 日绝对收益 < −20%（fwd 是小数，−0.20 = −20%）
    窗口   = full（全部 77 期）与 oos（第 24–76 期，对应 walk-forward 口径）
"""
import hashlib
import pickle

import numpy as np

from . import book_rules
from .paths import DATA_ROOT, PANEL_PKL

BAD_THRESH = -0.20
FWD_COL = 1                 # fwd[:,1] = 60 日
OOS_START = 24


def auc(score, bad):
    """AUC = P(好结果的分数 > 坏结果的分数)。>0.5 表示高分确实更安全。"""
    order = np.argsort(score, kind="mergesort")
    s, b = np.asarray(score)[order], np.asarray(bad, dtype=bool)[order]
    n = len(s)
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0 + 1
        i = j + 1
    n_good = int((~b).sum())
    n_bad = int(b.sum())
    if n_good == 0 or n_bad == 0:
        return float("nan")
    return float((ranks[~b].sum() - n_good * (n_good + 1) / 2.0) / (n_good * n_bad))


def _sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    except Exception:
        return None


def build(panel_path=None, bad_thresh=BAD_THRESH):
    """返回 {full: {...}, oos: {...}, meta: {...}}。"""
    panel_path = panel_path or PANEL_PKL
    with open(panel_path, "rb") as fh:
        P = pickle.load(fh)

    books = list(P["books"])
    idx = [books.index(b) for b in book_rules.CORE_BOOKS]

    comps, bads, dates = [], [], []
    for di, d in enumerate(P["data"]):
        comp = d["S"][:, idx].mean(axis=1)
        bad = d["fwd"][:, FWD_COL] < bad_thresh
        ok = ~(np.isnan(comp) | np.isnan(d["fwd"][:, FWD_COL]))
        comps.append(comp[ok])
        bads.append(bad[ok])
        dates.append(np.full(int(ok.sum()), di))
    comp = np.concatenate(comps)
    bad = np.concatenate(bads)
    di = np.concatenate(dates)

    out = {"meta": {
        "panel": str(panel_path),
        "panel_sha256": _sha(panel_path),
        "scorer_sha256": _sha(DATA_ROOT / "bt_scorer.py"),
        "bad_thresh": bad_thresh,
        "horizon_days": 60,
        "core_books": list(book_rules.CORE_BOOKS),
        "n_total": int(len(comp)),
        "windows": {},
    }}

    for tag, mask_di in (("full", np.ones_like(di, dtype=bool)), ("oos", di >= OOS_START)):
        m = mask_di
        c, b = comp[m], bad[m]
        rates, edges = _quintiles(c, b)
        out[tag] = {
            "n": int(len(c)),
            "base_bad_rate": round(float(b.mean()) * 100, 2),
            "auc": round(auc(c, b), 4),
            "quintiles": [round(x, 2) for x in rates],
            "quintile_edges": [round(float(e), 2) for e in edges],
            "bins": _bins(c, b, width=5),
        }
        out["meta"]["windows"][tag] = {
            "n": int(len(c)),
            "from": str(P["dates"][0]) if tag == "full" else str(P["dates"][OOS_START]),
            "to": str(P["dates"][-1]),
        }
    return out


def _quintiles(c, b, k=5):
    """按排名切五等分（不能用 np.quantile —— 并列会产生空箱）。"""
    order = np.argsort(c, kind="mergesort")
    n = len(order)
    rates, edges = [], []
    for qi in range(k):
        lo = qi * n // k
        hi = (qi + 1) * n // k if qi < k - 1 else n
        seg = order[lo:hi]
        rates.append(float(b[seg].mean()) * 100)
        edges.append(float(c[seg[0]]))
    return rates, edges


def _bins(c, b, width=5, max_bins=40):
    lo = int(np.floor(c.min() / width) * width)
    hi = int(np.ceil(c.max() / width) * width)
    bins = []
    for x in range(lo, hi, width):
        m = (c >= x) & (c < x + width)
        n = int(m.sum())
        if n == 0:
            continue
        bins.append({"lo": x, "hi": x + width, "n": n,
                     "bad_rate": round(float(b[m].mean()) * 100, 2)})
    if len(bins) > max_bins:                      # 分数跨度过大时合并相邻桶
        step = len(bins) // max_bins + 1
        bins = bins[::step]
    return bins


def lookup(table, core, window="oos"):
    """查该核心分所在分桶的历史坏率。"""
    w = table.get(window) or table.get("full")
    if not w:
        return None
    seg = None
    for x in w.get("bins", []):
        if x["lo"] <= core < x["hi"]:
            seg = x
            break
    if seg is None:                                # 超出桶范围 → 取最近的一桶
        bins = w.get("bins") or []
        if not bins:
            return None
        seg = min(bins, key=lambda x: abs((x["lo"] + x["hi"]) / 2 - core))
    qi = 0
    for i, e in enumerate(w.get("quintile_edges", [])):
        if core >= e:
            qi = i
    return {
        "bin_lo": seg["lo"], "bin_hi": seg["hi"], "n": seg["n"],
        "bad_rate": seg["bad_rate"], "n_in_bin": seg["n"],
        "quintile": f"Q{qi + 1}",
        "quintile_bad_rate": w["quintiles"][qi] if qi < len(w["quintiles"]) else None,
        "base_bad_rate": w["base_bad_rate"], "auc": w["auc"],
        "window": window, "n_window": w["n"],
    }
