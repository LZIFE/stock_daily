#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""极简 .env 加载（无第三方依赖）：KEY=VALUE，# 注释"""
import os


def load_env(path=None):
    path = path or os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
