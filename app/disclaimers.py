"""免责与偏差清单 —— 单一出处，随每次响应返回。

原则：**偏差要跟着数字走**，不能只写在页脚。
每条都对应一个实测证据，见 SCORING_V2.md 与对抗性审查报告。
"""

BASE = [
    "本系统输出「条件是否满足」，不是预期收益，不构成投资建议。",
    "数据为离线快照，非实时行情。",
    "股票池不含已退市股票 → 历史坏率是下界，正面结论被高估（负面结论更稳健）。",
    "未做行业/市值中性化：核心分高分组集中在低估值红利（高速/港口/公用事业），是风格暴露而非 alpha。",
    "4 本核心分相对 29 本等权的改进在统计上不显著（置信区间跨 0）。",
    "未计入交易成本（约 0.2–0.3%/月，与效应量级同阶）。",
    "规则是对书本观点的蒸馏近似，结论仅在「这套规则实现」层面成立。",
]

# 按状态追加
EXTRA = {
    "pe_missing": "PE 不适用（亏损或利润/营收背离被规则置空），估值维度仅由 PB 支撑 —— 该分数不代表它看起来像的意思。",
    "loss_maker": "该公司近 12 个月为亏损，PE 无法计算。",
    "quality_bad": "quality_bad：利润与营收背离，规则已主动将 PE 置空。",
    "low_coverage": "核心字段覆盖不足，判定可靠性下降。",
    "liquid": "成交额偏低：仅压低仓位上限，不代表更危险（实证该信号显著反向）。",
    "ties": "核心分取值高度离散且存在大量并列，分位是区间不是排名，不可理解为精确名次。",
    "ai": "AI 解读层未经回测验证，且不得改变判定；其中引用的公告内容未经独立核实。",
}


def for_record(rec, include_ai=False):
    """按记录状态拼装应显示的免责条目。"""
    out = list(BASE)
    if rec.get("pe_available") is False:
        out.append(EXTRA["pe_missing"])
    if rec.get("loss_maker"):
        out.append(EXTRA["loss_maker"])
    if rec.get("quality_bad"):
        out.append(EXTRA["quality_bad"])
    imputed = rec.get("core_imputed_books") or []
    if imputed:
        out.append(
            f"核心分中有 {len(imputed)}/4 本书（{'、'.join(imputed)}）因数据缺失而使用兜底值参与计算；"
            f"保留兜底是为了与回测口径一致（改掉就失去证据链），但这意味着该核心分并非完全由真实输入得出。")
    if (rec.get("core_coverage_pct") or 100) < 100:
        out.append(EXTRA["low_coverage"])
    if "流动性受限" in (rec.get("flags") or []):
        out.append(EXTRA["liquid"])
    if (rec.get("n_tied") or 0) > 1:
        out.append(EXTRA["ties"])
    if include_ai:
        out.append(EXTRA["ai"])
    return out
