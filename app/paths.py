"""路径解析。

本包位于 <工作区>/automation_stock_analyse/app/。
数据与算分规则（bt_scorer.py / bt_cache_long/）都在工作区根目录。
根目录不是 git 仓库，所以只能靠路径解析去拿。

目录布局：
    <DATA_ROOT>/                      工作区根目录（默认 = 仓库上一级）
        bt_scorer.py                  29 本规则（唯一事实来源）
        bt_cache_long/<code>.json     4898 只：1700 根日K + PIT 财报
        bt_robust_data.pkl            77 期回测面板（用于历史坏率）
        _candidate_pool.json          4898 只代码→名称（覆盖率 100%）
        _all_stocks.json              1691 只（pe/pb/mv/sectors，用于补充）
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]          # automation_stock_analyse/
APP_ROOT = Path(__file__).resolve().parent               # app/

_env = os.environ.get("DATA_ROOT", "").strip()
DATA_ROOT = Path(_env) if _env else REPO_ROOT.parent     # 书本蒸馏/

CACHE_DIR = DATA_ROOT / "bt_cache_long"
PANEL_PKL = DATA_ROOT / "bt_robust_data.pkl"
POOL_JSON = DATA_ROOT / "_candidate_pool.json"
ALL_STOCKS_JSON = DATA_ROOT / "_all_stocks.json"

APP_DATA = APP_ROOT / "data"
SNAPSHOT_DIR = APP_DATA / "snapshot"
AI_CACHE_DIR = APP_DATA / "ai_cache"
EVENT_CACHE_DIR = APP_DATA / "event_cache"

CONFIG_JSON = REPO_ROOT / "config" / "score_weights_v2.json"


def ensure_scorer_importable():
    """把工作区根加入 sys.path，使 `import bt_scorer` 可用。

    注意：只有**构建期**（build_snapshot / verify_scoring）需要它。
    运行时只查快照，不需要 bt_scorer，也不需要那份 443M 缓存。
    """
    root = str(DATA_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return root


def sanity():
    """返回关键路径是否存在，供 /api/health 与 CLI 报错用。"""
    return {
        "DATA_ROOT": str(DATA_ROOT),
        "bt_scorer.py": (DATA_ROOT / "bt_scorer.py").exists(),
        "bt_cache_long": CACHE_DIR.is_dir(),
        "bt_robust_data.pkl": PANEL_PKL.exists(),
        "_candidate_pool.json": POOL_JSON.exists(),
        "config/score_weights_v2.json": CONFIG_JSON.exists(),
    }


if __name__ == "__main__":
    for k, v in sanity().items():
        print(f"  {'OK ' if v is True else ('MISSING' if v is False else '')}"
              f"{'':<8}{k}")
