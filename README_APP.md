# 29 本书观点 · 个股买入决策系统

输入一个 A 股代码，返回 29 本投资书的逐本观点，以及一个由**确定性规则**给出的判定。
AI 只做解读，**不得修改判定**。

## 快速开始

```bash
cd automation_stock_analyse
pip install -r requirements-app.txt

# 1) 构建快照（全市场 4898 只，约 2.5 分钟）
python -m app.build_snapshot

# 2) 启动（同时提供 API 与前端）
python -m uvicorn app.main:app --port 8000
# 打开 http://127.0.0.1:8000
```

前端开发模式（改代码热更新，API 走 Vite 代理）：

```bash
cd web && npm install && npm run dev     # http://localhost:5173
```

## 目录

```
app/
  paths.py          DATA_ROOT 解析（默认仓库上一级 = 工作区根）
  scoring.py        算分适配器（不实现规则，只调用根目录 bt_scorer.py）
  book_rules.py     29 本 × {规则原文, 依赖字段, 语义簇}
  xsec.py           横截面分位 + 分档
  badrate.py        分桶历史坏率（从回测面板现算）
  build_snapshot.py 两遍式构建 CLI
  snapshot.py       运行时查表（fail closed）
  config.py         分档阈值只从已验证的 v2 配置读
  disclaimers.py    免责与偏差清单（单一出处）
  schemas.py        API 契约（Pydantic）
  main.py           FastAPI 入口
  routers/          basic / analysis / events / interpretation
  ai/               client / events / prompt / interpreter / guard
  tools/            verify_scoring.py（parity 验收门）
web/                React + Vite + TS 前端
```

## 验收门：parity

```bash
python -m app.build_snapshot --asof 2026-07-31 --out app/data/snapshot/_verify
python -m app.tools.verify_scoring --snapshot app/data/snapshot/_verify
```

实测：4894 只 × 29 本 = 124,477 个分数点，与回测面板全部一致。

## 三条不可违背的约束

1. **规则只在根目录 `bt_scorer.py` 里**，本系统不复制任何规则。
2. **判定只能由规则引擎给出。** AI 输出经 `app/ai/guard.py` 服务端强制覆盖。
3. **算不出来的分数是 `null`，不是 50。** 核心分保留兜底值是为了与回测一致，
   但必须披露（见 `core_imputed_books`）。

## 已知局限

见 `app/disclaimers.py`。要点：不含退市股（坏率是下界）、未做行业/市值中性化、
4 本核心分的改进在统计上不显著、未计交易成本、核心分仅 199 个不同取值故不可排名。
