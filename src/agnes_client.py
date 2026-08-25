#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agnes AI 客户端（OpenAI 兼容接口）
Base: https://apihub.agnes-ai.com/v1  模型默认 agnes-2.0-flash
未配置 AGNES_API_KEY 时返回 None，主流程自动降级为纯规则报告。
"""
import os
import time

import requests

DEFAULT_BASE = "https://apihub.agnes-ai.com/v1"
DEFAULT_MODEL = "agnes-2.0-flash"

SYSTEM_PROMPT = """你是资深A股分析师，融合多位投资大师视角：格雷厄姆的安全边际、费舍/林奇的成长质量、\
马克斯的周期位置、怀科夫/安娜库林的量价确认、迈吉/道氏的趋势结构、卡尼曼的行为风控。

你会收到一份股票池日报数据：今日指数表现、以及按规则预分层的三档名单（强势回踩/深度回踩/追高风险）。

请输出一份简洁的中文盘后点评，结构如下（用纯文本+短横线列表，不要markdown表格）：
一、市场综述（2-3句：指数结构与资金风格）
二、强势回踩档点评（点名2-4只最值得关注的个股，说明逻辑与买点思路）
三、深度回踩档点评（哪些可以开始跟踪、需要等什么企稳信号）
四、风险提示（本周宏观变量、仓位纪律）

要求：观点必须基于给定数据，不编造数据；总长500字以内；结尾加一行免责声明。"""


def agnes_analyze(data_text, timeout=60):
    """调用 Agnes chat/completions，返回文本；失败/未配置返回 None"""
    key = os.environ.get("AGNES_API_KEY", "").strip()
    if not key:
        return None
    # 空字符串回退到默认值（GitHub Secret 留空时会传空串而非缺失）
    base = (os.environ.get("AGNES_BASE_URL") or DEFAULT_BASE).rstrip("/")
    model = (os.environ.get("AGNES_MODEL") or DEFAULT_MODEL)
    url = f"{base}/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": data_text},
        ],
        "temperature": 0.4,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    for attempt in range(3):  # 免费档有RPM限制，做退避重试
        try:
            r = requests.post(url, json=body, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            print(f"  [agnes] HTTP {r.status_code}: {r.text[:150]}")
            if r.status_code in (401, 403):
                return None  # key 无效，重试无意义
        except Exception as e:
            print(f"  [agnes] 第{attempt + 1}次失败: {e}")
        time.sleep(2 ** (attempt + 1))
    return None


if __name__ == "__main__":
    out = agnes_analyze("测试：上证指数 -0.59%，创业板指 -3.21%。")
    print(out or "(AGNES_API_KEY 未配置或调用失败)")
