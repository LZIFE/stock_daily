#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成全部 7 个模板的预览页（真实当日数据），输出 out/preview/index.html"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from env_loader import load_env                    # noqa: E402
from fetcher import fetch_indices, fetch_pool, load_pool, classify  # noqa: E402
from report_builder import build_html              # noqa: E402
from templates import LABELS                       # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "out", "preview")


def main():
    load_env()
    print("抓取行情（所有模板共用同一份当日数据）...")
    indices = fetch_indices()
    pool = fetch_pool(load_pool())
    data_date = indices[0]["date"]
    tiers = classify(pool, indices[0]["chg_today"])
    os.makedirs(OUT, exist_ok=True)

    blocks = []
    for name, label in LABELS.items():
        html_body = build_html(indices, tiers, None, data_date, template=name)
        f = os.path.join(OUT, f"{name}.html")
        with open(f, "w", encoding="utf-8") as fp:
            fp.write(html_body)
        print(f"  {label} -> {f}")
        blocks.append(f"""
<div style="margin:28px 0">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
    <span style="font-size:18px;font-weight:700">{label}</span>
    <code style="background:#1e293b;color:#7dd3fc;padding:2px 8px;border-radius:4px;font-size:12px">REPORT_TEMPLATE={name}</code>
    <a href="{name}.html" target="_blank" style="font-size:13px;color:#3b82f6">新窗口打开 ↗</a>
  </div>
  <iframe src="{name}.html" style="width:100%;height:1150px;border:1px solid #d1d5db;border-radius:10px;background:#fff"></iframe>
</div>""")

    index_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>模板预览 · 选择你的日报风格</title></head>
<body style="margin:0;background:#111827;font-family:-apple-system,'PingFang SC',sans-serif;color:#e5e7eb;padding:30px 0">
<div style="max-width:900px;margin:0 auto;padding:0 16px">
<h1 style="font-size:24px">📰 模板预览 · 7 种日报风格</h1>
<p style="color:#9ca3af;line-height:1.8">以下均为今日真实数据渲染。选定后：本地在 <code>.env</code> 写
<code>REPORT_TEMPLATE=名字</code>；线上把它加到 GitHub Secrets（或直接写进 workflow 的 env）。</p>
{''.join(blocks)}
</div></body></html>"""
    idx_file = os.path.join(OUT, "index.html")
    with open(idx_file, "w", encoding="utf-8") as fp:
        fp.write(index_html)
    print(f"\n预览页 -> {idx_file}")
    return idx_file


if __name__ == "__main__":
    path = main()
    import subprocess
    subprocess.run(["open", path])
