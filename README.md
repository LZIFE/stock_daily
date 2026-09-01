# A股加仓池日报自动化

每个交易日盘前自动：抓取行情 → 重算核心池66只技术位 → 规则分层 → Agnes AI 点评 → 邮件送达。

```
GitHub Actions (cron 工作日 07:30 北京时间)
   └─ main.py
        ├─ src/fetcher.py         新浪K线(主) + 东财(备)，算 MA20/MA60/60日位/量比
        ├─ src/agnes_client.py    Agnes AI（OpenAI兼容）生成盘后点评
        ├─ src/report_builder.py  HTML 报告（三档分层表）
        └─ src/mailer.py          SMTP 发信（QQ/163/Gmail 均可）
```

## 分层规则

| 档位 | 条件 | 含义 |
|---|---|---|
| ✅ 第一档 强势回踩 | 评分≥80 且 距MA60≥-5% 且 回踩MA20(-7%~+1.5%) 且 今日跑赢大盘 | 可分批关注 |
| ⏳ 第二档 深度回踩 | 评分≥75 且 (距MA20≤-4% 或 60日位≤25%) | 等企稳信号 |
| ⛔ 追高风险 | 60日位≥80% 或 放量+5日涨超10% | 不建议现价加仓 |

## 本地运行

```bash
pip install -r requirements.txt
cp .env.example .env      # 填入配置（可不填，先跑通看效果）
python main.py            # 报告输出到 out/report_<日期>.html
```

## 部署到 GitHub Actions

1. 把本文件夹作为独立仓库推送：
   ```bash
   cd automation_stock_analyse
   git init && git add . && git commit -m "init: daily stock report"
   git remote add origin git@github.com:<你>/<仓库名>.git
   git push -u origin main
   ```
2. 仓库 **Settings → Secrets and variables → Actions → New repository secret**，逐个添加：

   | Secret | 说明 | 必填 |
   |---|---|---|
   | `SMTP_HOST` | 如 `smtp.qq.com` | ✅ |
   | `SMTP_PORT` | `465` | ✅ |
   | `SMTP_USER` | 发件邮箱 | ✅ |
   | `SMTP_PASS` | **授权码**（不是登录密码；QQ邮箱：设置→账户→开启IMAP/SMTP→生成授权码） | ✅ |
   | `MAIL_TO` | 收件邮箱，多个用英文逗号分隔 | ✅ |
   | `AGNES_API_KEY` | platform.agnes-ai.com 控制台生成 | 选填 |
   | `AGNES_MODEL` / `AGNES_BASE_URL` | 有默认值，一般不用填 | 选填 |

3. 到 **Actions** 页面手动触发一次 `daily-stock-report`（workflow_dispatch）验证。
4. 之后每个交易日北京时间约 07:30 自动运行（GitHub cron 可能有十几分钟延迟，所以实际开始约 08:00）。

> 注意：`.github/workflows/` 必须位于仓库根目录——本文件夹已是完整仓库结构，直接整体推送即可。

## 模板风格（20选1）

先运行 `python3 preview_templates.py` 生成并打开全部风格的预览页（`out/preview/index.html`），
选定后在 `.env` 或 GitHub Secrets 里配置：

```bash
REPORT_TEMPLATE=vogue      # 已选定 ⑭ 时尚大片 THE POOL；不配置时也默认用它
```

| key | 风格 | key | 风格 |
|---|---|---|---|
| `classic` | ① 经典深蓝金融（原默认） | `focus` | ⑧ 今日聚焦 · Top3深读 |
| `terminal` | ② 终端暗黑风 | `letter` | ⑨ 订阅信件 · 书信叙事 |
| `editorial` | ③ 极简杂志风 | `dashboard` | ⑩ 数据驾驶舱 |
| `newspaper` | ④ 报纸风 | `changelog` | ⑪ 更新日志 |
| `imperial` | ⑤ 红金研报风 | `brew` | ⑫ 晨报简报 |
| `pastel` | ⑥ 清新卡片风 | `readme` | ⑬ 工程文档 |
| `swiss` | ⑦ 瑞士网格风 | `vogue` | ⑭ 时尚大片 ✅ **当前默认** |
| | | `journal` | ⑮ 手账涂鸦 |
| | | `zen` | ⑯ 日式侘寂 |
| | | `neon` | ⑰ 赛博朋克霓虹 |
| | | `arcade` | ⑱ 像素街机 |
| | | `luxe` | ⑲ 奢华黑金 |
| | | `infographic` | ⑳ 信息图数据新闻 |

> ⑧-⑳ 不仅换了视觉，**内容组织方式也不同**：书信体无表格、聚焦卡只深读Top3、
> 驾驶舱有池级KPI磁贴、信息图有涨跌分布条形图等。

## Agnes 说明

Agnes AI（apihub.agnes-ai.com）是 OpenAI 兼容的大模型接口，负责把当日数据写成点评，
**它不负责发邮件**；发信走 SMTP。未配置 `AGNES_API_KEY` 时程序照常运行，仅省略AI段落。

## 免责声明

本项目仅为个人数据整理与学习用途，不构成投资建议。
