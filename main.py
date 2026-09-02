#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股加仓池日报主流程：
抓行情 → 重算技术位 → 规则分层 → (可选)Agnes AI点评 → HTML邮件
未配置 SMTP 时：报告落盘 + 控制台输出，正常退出（方便先跑通再配密钥）。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from env_loader import load_env          # noqa: E402
from fetcher import fetch_indices, fetch_pool, load_pool, classify  # noqa: E402
from agnes_client import agnes_analyze   # noqa: E402
from report_builder import build_html, email_subject  # noqa: E402
from mailer import missing_config, send_html         # noqa: E402
try:
    from score_engine import evaluate_pool as _multi_eval  # noqa: E402
    MULTI_OK = True
except Exception:
    MULTI_OK = False

CST = timezone(timedelta(hours=8))
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")


def main():
    load_env()
    print("[1/4] 抓取行情...")
    indices = fetch_indices()
    if not indices:
        print("指数抓取失败，退出")
        return 1
    data_date = indices[0]["date"]
    bench = indices[0]["chg_today"]
    pool = fetch_pool(load_pool())
    ok_n = sum(1 for p in pool if not p.get("error"))
    print(f"      池内刷新成功 {ok_n}/{len(pool)}，数据日期 {data_date}")

    tiers = classify(pool, bench)
    print(f"[2/4] 分层: 第一档{len(tiers['tier_a'])} 第二档{len(tiers['tier_b'])} "
          f"追高{len(tiers['danger'])} 观察{len(tiers['watch'])}")

    # 多视角评分 (开关: MULTI_PERSPECTIVE=true)
    if os.environ.get("MULTI_PERSPECTIVE", "true").lower() == "true" and MULTI_OK:
        ctx = {"bench_chg_today": bench, "hwm_drawdown_pct": float(os.environ.get("HWM_DRAWDOWN", 0))}
        multi = _multi_eval(pool, ctx)
        # 把多视角总分合并回每只股票
        multi_map = {m["code"]: m for m in multi}
        for k in ("tier_a", "tier_b", "danger", "watch"):
            for r in tiers[k]:
                m = multi_map.get(r.get("code"))
                if m:
                    r["_multi_total"] = m["total"]
                    r["_multi_band"] = m["band"]
                    r["_multi_veto"] = m["veto"]
                    r["_position_cap"] = m["position_cap_pct"]
        top3 = sorted([m for m in multi if m["band"] == "tier_a"], key=lambda x: -x["total"])[:3]
        print(f"      多视角评分完成, tier_a 共 {sum(1 for m in multi if m['band']=='tier_a')} 只")
        if top3:
            top3_str = ", ".join("{0}({1:.0f})".format(m["name"], m["total"]) for m in top3)
            print("      Top3: " + top3_str)

    print("[3/4] AI 点评...")
    payload = json.dumps({
        "data_date": data_date,
        "indices": [{k: d[k] for k in ("name", "close", "chg_today", "pos60")} for d in indices],
        "tier_a": tiers["tier_a"], "tier_b": tiers["tier_b"], "danger": tiers["danger"],
    }, ensure_ascii=False)
    ai_text = agnes_analyze(payload)
    print("      Agnes 已生成点评" if ai_text else "      未启用AI（无key或调用失败），使用规则报告")

    html_body = build_html(indices, tiers, ai_text, data_date,
                           template=os.environ.get("REPORT_TEMPLATE", "vogue"))

    os.makedirs(OUT_DIR, exist_ok=True)
    out_file = os.path.join(OUT_DIR, f"report_{data_date}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_body)
    print(f"[4/4] 报告已生成 -> {out_file}")

    subject = email_subject(indices, data_date)
    miss = missing_config()
    if miss:
        print(f"[skip] 未配置邮件环境变量 {miss}，本次仅落盘不发送。"
              f"\n       本地可在 .env 填写；线上在 GitHub Secrets 填写。")
        return 0
    to = send_html(subject, html_body)
    print(f"邮件已发送 -> {to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
