"""横截面层。

核心分的分位、`pct_vol` / `pct_turn` / `amt_pctl` / `pe_pctl` / `pb_pctl`
全是**横截面量** —— 单只股票单独算没有意义，必须拿全市场当尺子。
这是本项目必须有「离线预计算 + 运行时查表」结构的根本原因。
"""
from collections import Counter
from .scoring import percentile_rank


def build_xsec(records):
    """从 Pass 1 的中间结果里抽出全市场排序向量。"""
    return {
        "vols": sorted(r["t"]["volat"] for r in records if r["t"].get("volat") is not None),
        "ams": sorted(r["amt20"] for r in records),
        "pes": sorted(r["f"]["pe"] for r in records
                      if r["f"].get("pe") is not None and r["f"]["pe"] > 0),
        "pbs": sorted(r["f"]["pb"] for r in records
                      if r["f"].get("pb") is not None and r["f"]["pb"] > 0),
    }


def assign_ranks(finals, cfg):
    """回填 core_pctl / n_tied / band。

    ⚠️ 并列实况（实测 4888 只）：核心分只有 **199 个不同取值**，
    平均并列块 24.6 只，最大 85 只，最高分 26 只并列。
    所以分位是**区间**不是排名 —— 这里只回填下界分位与并列只数，
    UI 必须显示 n_tied，绝不能显示「第 N 名」。

    实测三种分位口径（下界/中位秩/上界）的 band 分布几乎相同
    （486 / 486 / 493），故只用下界，不引入双分位的额外复杂度。
    """
    vals = sorted(f["core_score"] for f in finals)
    ties = Counter(f["core_score"] for f in finals)
    bands_cfg = cfg.get("bands", {})
    buy_pctl = bands_cfg.get("buy_pctl", 90)
    watch_pctl = bands_cfg.get("watch_pctl", 70)
    min_cov = cfg.get("coverage", {}).get("min_coverage_pct", 40)

    from .scoring import band as band_fn
    for f in finals:
        f["core_pctl"] = round(percentile_rank(vals, f["core_score"]), 2)
        f["n_tied"] = ties[f["core_score"]]
        f["band"] = band_fn(f["core_pctl"], f["soft_demote"], f["hard_veto"],
                            f["core_coverage_pct"], min_cov, buy_pctl, watch_pctl)
        # 仓位层：流动性受限只压上限，不改判定
        cap = cfg.get("position_layer", {}).get("base_cap_pct", 10.0)
        if "流动性受限" in f["flags"]:
            cap = min(cap, cfg.get("executability", {})
                             .get("liquidity_floor", {}).get("cap_pct", 5.0))
        f["position_cap_pct"] = cap
    return finals
