"""29 本书的规则元数据。

用途：
  1. UI 展示每本书「在用什么规则、被哪个数据点触发」——否则 29 个分数是黑箱
  2. 判定某本书是否真的可算：`fields` 里任一字段为 None → 标 unavailable，
     绝不能把「算不出来」的 50 当成真实分数展示
  3. 区分「有预测证据」的 4 本与「仅观点展示」的其余 25 本

规则文本严格对照工作区根 bt_scorer.py 的 books20() / books9_new() 实现。
若 bt_scorer.py 改动，本文件必须同步（verify_scoring 会校验书本集合一致）。
"""

# 核心 4 本：在分类目标上被 walk-forward 验证过（纯样本外 Q1−Q5 14.84pp / AUC 0.6492）
CORE_BOOKS = ["邱国鹭", "舍夫林·行为", "格雷厄姆", "达利欧"]

# 语义簇（用于 UI 分组展示，以及说明「29 本并非 29 个独立观点」）
CLUSTERS = {
    "价值便宜": "便宜（PE/PB 低）",
    "质量护城河": "高毛利 / 高 ROE / 现金利润质量",
    "成长": "净利与营收增速",
    "趋势动量": "均线排列与位置",
    "量价情绪": "量比、K 线、资金",
    "周期逆向": "位置低 + 回撤深",
    "尾部风险": "回撤、波动、凸性",
    "低波动": "低振幅 / 低波动率",
    "流动性能力圈": "成交额规模",
}

BOOKS = {
    "格雷厄姆": dict(
        cluster="价值便宜", core=True,
        rule="PE<15 +25；PE<25 +10；PE>60 −20。PB<1.5 +15；PB<3 +5；PB>6 −15。",
        tech=[], fin=["pe", "pb"], xsec=[]),
    "唐朝": dict(
        cluster="质量护城河", core=False,
        rule="ROE>15 +20；>10 +10；<5 −15。毛利率>30 +10；<15 −10。负债率>70 −15；<40 +5。",
        tech=[], fin=["roe", "gm", "debt"], xsec=[]),
    "迈吉·趋势": dict(
        cluster="趋势动量", core=False,
        rule="价≥MA60 +20 否则 −20；价≥MA20 +10 否则 −10。60日位置 30~70 +15；>85 −10。",
        tech=["ma20", "ma60", "pos60"], fin=[], xsec=[]),
    "马克斯·周期": dict(
        cluster="周期逆向", core=False,
        rule="60日位置≤55 +15；>85 −20。60日回撤>15 +10。",
        tech=["pos60", "dd60"], fin=[], xsec=[]),
    "怀科夫·量价": dict(
        cluster="量价情绪", core=False,
        rule="量比>1.3 且当日涨 +20；量比>1.3 +10；量比<0.7 −10。",
        tech=["vol_ratio"], fin=[], xsec=[], uses_chg=True),
    "费舍·成长": dict(
        cluster="成长", core=False,
        rule="净利同比>30 +25；>10 +15；<0 −20。营收同比>20 +10；<0 −20。quality_bad −30。",
        tech=[], fin=["np_yoy", "rev_yoy", "quality_bad"], xsec=[]),
    "达摩达兰·PEG": dict(
        cluster="价值便宜", core=False,
        rule="PEG=PE/净利同比：<0.5 +30；<1 +20；<1.5 +5；否则 −15。quality_bad −30。",
        tech=[], fin=["pe", "np_yoy", "quality_bad"], xsec=[]),
    "蜡烛图·K线": dict(
        cluster="量价情绪", core=False,
        rule="近5日阳线≥4 +25；≥3 +15；≤1 −15。",
        tech=["yang5"], fin=[], xsec=[]),
    "金融怪杰·风控": dict(
        cluster="尾部风险", core=False,
        rule="60日回撤>10 +15；>5 +5。近5日涨幅 0~15 +10；>25 −15。",
        tech=["dd60", "up5"], fin=[], xsec=[]),
    "芒格·能力圈": dict(
        cluster="流动性能力圈", core=False,
        rule="20日均成交额>50亿 +15；>10亿 +5；<2亿 −10。",
        tech=[], fin=[], xsec=[], uses_amount=True),
    "舍夫林·行为": dict(
        cluster="低波动", core=True,
        rule="60日平均振幅≤4 +15；>8 −15。（其余区间维持 50）",
        tech=["amp60"], fin=[], xsec=[]),
    "缠论": dict(
        cluster="趋势动量", core=False,
        rule="MA20>MA60 +20；DIF>0 +15；60日位置<30 −10。",
        tech=["ma20", "ma60", "dif", "pos60"], fin=[], xsec=[]),
    "道氏理论": dict(
        cluster="趋势动量", core=False,
        rule="价≥MA60 +20；价≥MA20 +10；位置 30~75 +10；量比>1.1 且涨 +10。",
        tech=["ma60", "ma20", "pos60", "vol_ratio"], fin=[], xsec=[], uses_chg=True),
    "彼得林奇": dict(
        cluster="成长", core=False,
        rule="净利同比>30 +20；>10 +10；<0 −15。营收同比>20 +10；<0 −15。quality_bad −25。"
             "PEG<1 +10；PE>50 −10。",
        tech=[], fin=["np_yoy", "rev_yoy", "pe", "quality_bad"], xsec=[]),
    "格雷厄姆多德": dict(
        cluster="价值便宜", core=False,
        rule="PB<1 +25；<1.5 +15；<3 +5；>6 −10。PE<10 +10。负债<40 +10；>70 −10。ROE>12 +5。",
        tech=[], fin=["pb", "pe", "debt", "roe"], xsec=[]),
    "卡尼曼": dict(
        cluster="低波动", core=False,
        rule="60日位置>85 −20；近5日涨>20 −15；振幅>8 −10；位置 20~60 +15。",
        tech=["pos60", "up5", "amp60"], fin=[], xsec=[]),
    "马尔基尔": dict(
        cluster="价值便宜", core=False,
        rule="PE>60 −25；PE<20 +15。PB>6 −10。位置>85 −10；量比>2.5 −5。",
        tech=["pos60", "vol_ratio"], fin=["pe", "pb"], xsec=[]),
    "安娜库林": dict(
        cluster="量价情绪", core=False,
        rule="量比>1.2 且涨 +20；量比<0.8 且涨 −15；量比>1.3 且跌 −10；位置 20~60 且量比>1 +10。",
        tech=["vol_ratio", "pos60"], fin=[], xsec=[], uses_chg=True),
    "缠中说禅": dict(
        cluster="趋势动量", core=False,
        rule="近5日涨>20 −20；60日回撤>10 +15；位置>80 −10；振幅≤5 +10。",
        tech=["up5", "dd60", "pos60", "amp60"], fin=[], xsec=[]),
    "趋势投资": dict(
        cluster="趋势动量", core=False,
        rule="MA20>MA60 +20；价≥MA60 +15；位置 30~75 +10；近5日涨 0~12 +5。",
        tech=["ma20", "ma60", "pos60", "up5"], fin=[], xsec=[]),
    "巴菲特": dict(
        cluster="质量护城河", core=False,
        rule="经营现金流/净利>1.2 +25；>0.8 +10；<0.4 −20。ROE>15 +15；>10 +5。"
             "PE<20 +10；>40 −15。负债>70 −15。",
        tech=[], fin=["ocf_ttm", "np_ttm", "roe", "pe", "debt"], xsec=[]),
    "塔勒布": dict(
        cluster="尾部风险", core=False,
        rule="回撤>25 且价≥MA20 +20；回撤>15 且20日涨>0 +12。负债<40 +10；>65 −20。"
             "年化波动>60 −15；60日涨>80 −15。",
        tech=["dd60", "ma20", "up20", "volat", "up60"], fin=["debt"], xsec=[]),
    "达利欧": dict(
        cluster="低波动", core=True,
        rule="波动率分位<20 +25；<40 +12；>80 −15。价≥MA60×0.95 +10。负债<50 +8。",
        tech=["volat", "ma60"], fin=["debt"], xsec=["vol"]),
    "索罗斯": dict(
        cluster="尾部风险", core=False,
        rule="回撤>20 且量比>1.3 且20日涨>0 +25；回撤>15 且20日涨>0 +12。"
             "MA20斜率>1.5 +10；<−2 −15。位置>90 −15。",
        tech=["dd60", "vol_ratio", "up20", "ma20_slope", "pos60"], fin=[], xsec=[]),
    "邱国鹭": dict(
        cluster="价值便宜", core=True,
        rule="PE<15 +20；<25 +8。PB<2 +12；>5 −12。成交额分位>85 −15（拥挤）；<40 +8。"
             "负债<40 +8。quality_bad −15。",
        tech=[], fin=["pe", "pb", "debt", "quality_bad"], xsec=["amt"]),
    "张磊": dict(
        cluster="质量护城河", core=False,
        rule="毛利率>45 +20；>30 +10；<12 −12。ROE>18 +15；>12 +8。净利同比>15 +8；<−10 −12。"
             "PE>60 −15。",
        tech=[], fin=["gm", "roe", "np_yoy", "pe"], xsec=[]),
    "多尔西": dict(
        cluster="质量护城河", core=False,
        rule="毛利率>40 +18；ROE>15 +12。负债>60 −12。PE<30 +8；>50 −12。振幅>7 −8。",
        tech=["amp60"], fin=["gm", "roe", "debt", "pe"], xsec=[]),
    "墨菲": dict(
        cluster="趋势动量", core=False,
        rule="MA5>MA20>MA60 +25；MA20>MA60 +10。DIF>0 +10。价≥MA20 +8 否则 −12。回撤>30 −12。",
        tech=["ma5", "ma20", "ma60", "dif", "dd60"], fin=[], xsec=[]),
    "纳瓦尔": dict(
        cluster="质量护城河", core=False,
        rule="毛利率>50 +20；>30 +8。ROE>15 +10。营收同比>20 +8；<0 −10。",
        tech=[], fin=["gm", "roe", "rev_yoy"], xsec=[]),
}

# 顺序（与 bt_scorer.ALL29 一致，verify_scoring 会校验）
ORDER = ["格雷厄姆", "唐朝", "迈吉·趋势", "马克斯·周期", "怀科夫·量价", "费舍·成长",
         "达摩达兰·PEG", "蜡烛图·K线", "金融怪杰·风控", "芒格·能力圈", "舍夫林·行为",
         "缠论", "道氏理论", "彼得林奇", "格雷厄姆多德", "卡尼曼", "马尔基尔",
         "安娜库林", "缠中说禅", "趋势投资", "巴菲特", "塔勒布", "达利欧", "索罗斯",
         "邱国鹭", "张磊", "多尔西", "墨菲", "纳瓦尔"]

CONSENSUS_BOOKS = [b for b in ORDER if b != "马尔基尔"]  # 马尔基尔是随机漫步制衡项，不进共识


def meta(name):
    """返回单本书的元数据（含 core / cluster 展示名）。"""
    m = dict(BOOKS.get(name, {}))
    m["name"] = name
    m["core"] = name in CORE_BOOKS
    m["cluster_label"] = CLUSTERS.get(m.get("cluster", ""), m.get("cluster", ""))
    m.setdefault("tech", [])
    m.setdefault("fin", [])
    m.setdefault("xsec", [])
    return m
