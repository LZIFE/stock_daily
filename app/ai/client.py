"""LLM 客户端。

复用仓库已有的凭证约定（.env 里的 OPENAI_* 优先 → AGNES_* 兜底），
但**不用** `merged/research.py:resolve_client()` 的客户端实例 —— 那个 timeout=75s，
实测不够（Agnes 经代理延迟 12.5s / 22s / 25s / 56s / >75s 都出现过）。

未配置或不可用时返回 (None, None)，调用方**必须**降级为纯规则报告，不得编造。
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from ..paths import REPO_ROOT

_TIMEOUT = 120          # 实测 >75s 出现过，给足余量
_PROBE_TTL = 300
_state = {"at": 0.0, "client": None, "model": None, "desc": None}


def _load_env():
    """把 .env 填进 os.environ（不覆盖已存在的）。"""
    for p in (REPO_ROOT / ".env", Path.cwd() / ".env"):
        if not p.exists():
            continue
        try:
            for ln in p.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                k, v = ln.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v:
                    os.environ.setdefault(k, v)
        except Exception:
            pass


def _is_placeholder(v):
    return any(m in (v or "").lower() for m in ("xxxx", "your_", "example", "replace_me"))


def _candidates():
    out = []
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k and not _is_placeholder(k):
        out.append(("DeepSeek", k,
                    os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.deepseek.com/v1",
                    os.environ.get("OPENAI_MODEL", "").strip() or "deepseek-chat"))
    k = os.environ.get("AGNES_API_KEY", "").strip()
    if k and not _is_placeholder(k):
        out.append(("Agnes", k,
                    os.environ.get("AGNES_BASE_URL", "").strip() or "https://apihub.agnes-ai.com/v1",
                    os.environ.get("AGNES_MODEL", "").strip() or "agnes-2.5-flash"))
    return out


def resolve(force=False):
    """返回 (client, model)。不可用时 (None, None)。结果缓存 5 分钟。"""
    now = time.time()
    if not force and _state["client"] and now - _state["at"] < _PROBE_TTL:
        return _state["client"], _state["model"]

    _load_env()
    try:
        from openai import OpenAI
    except Exception:
        _state.update({"at": now, "client": None, "model": None, "desc": "openai SDK 未安装"})
        return None, None

    for label, key, base, model in _candidates():
        try:
            c = OpenAI(api_key=key, base_url=base, timeout=_TIMEOUT, max_retries=0)
            c.chat.completions.create(model=model,
                                      messages=[{"role": "user", "content": "ping"}],
                                      max_tokens=4, temperature=0)
            _state.update({"at": now, "client": c, "model": model, "desc": f"{label}/{model}"})
            return c, model
        except Exception:
            continue
    _state.update({"at": now, "client": None, "model": None, "desc": "无可用 LLM"})
    return None, None


def probe():
    """返回 (bool, model|None)。给 /api/health 用。"""
    c, m = resolve()
    return bool(c), m


def complete(system, user, max_tokens=2500, temperature=0.2):
    """返回 (text, model)。失败返回 (None, model)。

    max_tokens 实测：2000 不够（输出 2455–3531 token 被截断 → JSON 残缺）。
    """
    c, m = resolve()
    if not c:
        return None, None
    try:
        r = c.chat.completions.create(
            model=m, temperature=temperature, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}])
        return (r.content if hasattr(r, "content") else r.choices[0].message.content), m
    except Exception:
        return None, m
