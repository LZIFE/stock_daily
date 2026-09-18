"""配置：分档阈值与门禁参数从已验证的 v2 配置读取，不另起一套。

原则：**凡是回测验证过的参数，只从一个地方读**（config/score_weights_v2.json）。
本文件不复制数值，只提供带默认值的读取，避免两处漂移。
"""
import json
import os

from .paths import CONFIG_JSON


def _load():
    try:
        with open(CONFIG_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


_CFG = _load()


def buy_pctl():
    return float(_CFG.get("bands", {}).get("buy_pctl", 90))


def watch_pctl():
    return float(_CFG.get("bands", {}).get("watch_pctl", 70))


def min_core_coverage():
    """核心 4 本字段覆盖率下限，低于此值不出判定（NO_DATA）。"""
    return float(os.environ.get("APP_MIN_CORE_COVERAGE")
                 or _CFG.get("coverage", {}).get("min_coverage_pct", 40))


def veto_rules():
    return _CFG.get("veto_rules", {})


def liquidity_floor():
    """流动性门槛 —— 只作标注并压低仓位上限，**不得否决**（实证显著反向）。"""
    ex = _CFG.get("executability", {}).get("liquidity_floor", {})
    return float(ex.get("amt20", 5e7)), float(ex.get("cap_pct", 5.0))


def config_hash():
    import hashlib
    return hashlib.sha256(
        json.dumps(_CFG, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def raw():
    return _CFG
