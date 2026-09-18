#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行情数据抓取 + 技术位计算
K线双源：新浪（主）→ 东财（备）。全部走 HTTP，绕过系统代理。
"""
import csv
import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone

import requests

CST = timezone(timedelta(hours=8))
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"}

_session = requests.Session()
_session.trust_env = False  # 本机系统代理会拦截国内站点，直连


def _sym(code):
    return ("sh" if code.startswith(("6", "9")) else "sz") + code


# ---------- 新浪日K ----------
def _kline_sina(sym, datalen=130):
    url = (
        "http://quotes.sina.cn/cn/api/jsonp_v2.php/var%20d=/"
        f"CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen={datalen}"
    )
    r = _session.get(url, headers=HEADERS, timeout=10)
    m = re.search(r"\((\[.*\])\)", r.text, re.S)
    if not m:
        raise ValueError(f"sina no json: {sym}")
    arr = json.loads(m.group(1))
    return [[x["day"][:10], float(x["open"]), float(x["high"]),
             float(x["low"]), float(x["close"]), float(x["volume"])] for x in arr]


# ---------- 东财日K（备源，字段顺序 date,open,close,high,low,volume）----------
def _kline_east(sym, datalen=130):
    code = sym[2:]
    secid = ("1." if sym.startswith("sh") else "0.") + code
    url = (
        "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={secid}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56"
        f"&klt=101&fqt=1&end=20500101&lmt={datalen}"
    )
    r = _session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = r.json()["data"]["klines"]
    out = []
    for line in data:
        d, o, c, h, l, v = line.split(",")[:6]
        out.append([d, float(o), float(h), float(l), float(c), float(v)])
    if len(out) < 61:
        raise ValueError(f"east kline too short: {sym}")
    return out


def fetch_kline(sym, retries=3, datalen=130):
    """返回 [[date, open, high, low, close, volume], ...]，新浪失败自动切东财"""
    last_err = None
    for i in range(retries):
        try:
            return _kline_sina(sym, datalen)
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (i + 1))
    try:
        return _kline_east(sym, datalen)
    except Exception:
        raise RuntimeError(f"{sym} 双源均失败: {last_err}")


# ---------- 技术位 ----------
def calc_tech(k):
    closes = [r[4] for r in k]
    vols = [r[5] for r in k]
    n = len(closes)

    def ma(w):
        return sum(closes[-w:]) / w if n >= w else None

    ma20, ma60 = ma(20), ma(60)
    h60 = max(r[2] for r in k[-60:])
    l60 = min(r[3] for r in k[-60:])
    c = closes[-1]
    pos60 = (c - l60) / (h60 - l60) * 100 if h60 > l60 else 50.0
    dd60 = (h60 - c) / h60 * 100
    v5 = sum(vols[-5:]) / 5
    v20 = sum(vols[-20:]) / 20 if n >= 20 else v5

    # ---- v2 评分体系新增（全部由已有 130 根日K推出，纯增量，不改动上面任何键）----
    # 近 5 日阳线数（蜡烛图·K线）
    yang5 = sum(1 for r in k[-5:] if r[4] > r[1])
    # 60 日平均振幅（舍夫林·行为：低波动偏好）
    amp60 = sum((r[2] - r[3]) / r[3] * 100 for r in k[-60:] if r[3] > 0) / max(1, min(n, 60))
    # 20 日日均成交额（邱国鹭「不拥挤」的拥挤度代理，因无流通股本无法算真换手率）
    amt20 = sum(r[5] * r[4] for r in k[-20:]) / max(1, min(n, 20))

    def _ema(vals, span):
        kk = 2 / (span + 1)
        e = vals[0]
        for v in vals[1:]:
            e = v * kk + e * (1 - kk)
        return e
    dif = (_ema(closes, 12) - _ema(closes, 26)) if n >= 26 else None
    # 60 日年化波动率（达利欧/塔勒布用）
    if n >= 60:
        rets = [math.log(closes[i] / closes[i - 1])
                for i in range(-60, 0) if closes[i - 1] > 0]
        if rets:
            mu = sum(rets) / len(rets)
            var = sum((x - mu) ** 2 for x in rets) / len(rets)
            volat = (var ** 0.5) * math.sqrt(250) * 100
        else:
            volat = None
    else:
        volat = None

    return {
        "date": k[-1][0],
        "close": round(c, 3),
        "chg_today": round((c / closes[-2] - 1) * 100, 2),
        "chg5": round((c / closes[-6] - 1) * 100, 2) if n >= 6 else None,
        "ma20": round(ma20, 3) if ma20 else None,
        "ma60": round(ma60, 3) if ma60 else None,
        "vs_ma20": round((c / ma20 - 1) * 100, 1) if ma20 else None,
        "vs_ma60": round((c / ma60 - 1) * 100, 1) if ma60 else None,
        "pos60": round(pos60, 1),
        "dd60": round(dd60, 1),
        "vol_ratio": round(v5 / v20, 2) if v20 else 1.0,
        # v2 新增字段
        "yang5": yang5,
        "amp60": round(amp60, 2),
        "amt20": round(amt20, 1),
        "dif": round(dif, 4) if dif is not None else None,
        "volat": round(volat, 1) if volat is not None else None,
    }


# ---------- 指数 ----------
INDEX_LIST = [("上证指数", "sh000001"), ("深成指", "sz399001"),
              ("创业板指", "sz399006"), ("科创50", "sh000688")]


def fetch_indices():
    out = []
    for name, sym in INDEX_LIST:
        try:
            t = calc_tech(fetch_kline(sym, datalen=70))
            out.append({"name": name, **t})
        except Exception as e:
            print(f"  [warn] 指数 {name} 失败: {e}")
    return out


# ---------- 股票池 ----------
POOL_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "pool_core.csv")


def load_pool(path=None):
    path = path or POOL_CSV
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            code = r["代码"].strip()
            rows.append({
                "code": code,
                "name": r["名称"].replace(" ", ""),
                "base_price": float(r["现价"]),
                "base_date": "2026-08-10",
                "pe_base": float(r["PE"]),
                "np_yoy": float(r["净利同比%"]),
                "rev_yoy": float(r["营收同比%"]),
                "roe": float(r["ROE%"]),
                "gm": float(r["毛利率%"]),
                "score": int(r["评分"]),
            })
    return rows


def fetch_pool(pool):
    """逐股刷新K线并合并技术位；失败保留原行并打标"""
    out = []
    for p in pool:
        sym = _sym(p["code"])
        try:
            t = calc_tech(fetch_kline(sym))
            pe_now = p["pe_base"] * t["close"] / p["base_price"]
            out.append({**p, **t,
                        "pe_now": round(pe_now, 1),
                        "since_base": round((t["close"] / p["base_price"] - 1) * 100, 1)})
        except Exception as e:
            print(f"  [warn] {p['name']} 失败: {e}")
            out.append({**p, "error": str(e)[:60]})
    return out


# ---------- 分层规则（与人工分析口径一致）----------
def classify(rows, bench_chg):
    """tier_a 强势回踩 / tier_b 深度回踩 / danger 追高风险 / watch 观察"""
    tiers = {"tier_a": [], "tier_b": [], "danger": [], "watch": []}
    for r in rows:
        if r.get("error"):
            tiers["watch"].append(r)
            continue
        rs_ok = r["chg_today"] >= bench_chg - 1.0          # 相对强度：基本跟住大盘或更强
        trend_ok = (r["vs_ma60"] or -99) >= -5             # 趋势未破
        pullback_ok = -7 <= (r["vs_ma20"] or 0) <= 1.5     # 回踩到MA20附近、未追高
        if r["pos60"] >= 80 or (r["vol_ratio"] >= 2 and r["chg5"] > 10):
            tiers["danger"].append(r)
        elif r["score"] >= 80 and trend_ok and pullback_ok and rs_ok:
            tiers["tier_a"].append(r)
        elif r["score"] >= 75 and ((r["vs_ma20"] or 0) <= -4 or r["pos60"] <= 25):
            tiers["tier_b"].append(r)
        else:
            tiers["watch"].append(r)
    for k in tiers:
        tiers[k].sort(key=lambda x: x.get("vs_ma20") if x.get("vs_ma20") is not None else 0)
    return tiers


if __name__ == "__main__":
    idx = fetch_indices()
    pool = fetch_pool(load_pool())
    bench = idx[0]["chg_today"] if idx else 0
    tiers = classify(pool, bench)
    now = datetime.now(CST)
    print(json.dumps({"now": now.isoformat(), "indices": idx,
                      "counts": {k: len(v) for k, v in tiers.items()}},
                     ensure_ascii=False, indent=2)[:800])
