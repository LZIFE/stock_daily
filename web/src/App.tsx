import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import type { Analysis, HealthOut, Interpretation, SnapshotMeta } from './types'
import SearchBar from './components/SearchBar'
import Section from './components/Section'
import Verdict from './components/Verdict'
import HistoryChart from './components/HistoryChart'
import EvidencePanel from './components/EvidencePanel'
import ThresholdPanel from './components/ThresholdPanel'
import ClusterPanel from './components/ClusterPanel'
import BooksPanel from './components/BooksPanel'
import AIPanel from './components/AIPanel'
import EventsPanel from './components/EventsPanel'
import Disclaimers from './components/Disclaimers'

function initialCode(): string {
  return new URLSearchParams(location.search).get('code') || ''
}

/**
 * 数据基准日距今天数。
 * 分级告警是必要的：这套分数会随快照老化而失效，而界面上每个数字看起来都一样「新鲜」，
 * 不提醒的话很容易拿三个月前的判定当今天的用。
 */
function daysSince(d?: string | null): number | null {
  if (!d) return null
  const t = new Date(d + 'T00:00:00').getTime()
  if (Number.isNaN(t)) return null
  return Math.floor((Date.now() - t) / 86400000)
}

const FACT = { tag: '已回测验证', tagSub: '事实层' } as const

export default function App() {
  const [health, setHealth] = useState<HealthOut | null>(null)
  const [meta, setMeta] = useState<SnapshotMeta | null>(null)
  const [bootErr, setBootErr] = useState<string | null>(null)

  const [code, setCode] = useState(initialCode)
  const [a, setA] = useState<Analysis | null>(null)
  const [aErr, setAErr] = useState<string | null>(null)
  const [loadingA, setLoadingA] = useState(false)

  const [ai, setAi] = useState<Interpretation | null>(null)
  const [aiErr, setAiErr] = useState<string | null>(null)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    Promise.all([api.health(), api.meta()])
      .then(([h, m]) => { setHealth(h); setMeta(m) })
      .catch(e => setBootErr(String(e.message || e)))
  }, [])

  useEffect(() => {
    if (!code) return
    let alive = true
    setLoadingA(true); setAErr(null); setA(null); setAi(null); setAiErr(null)
    api.analysis(code)
      .then(r => alive && setA(r))
      .catch(e => alive && setAErr(String(e.message || e)))
      .finally(() => alive && setLoadingA(false))
    const url = new URL(location.href)
    url.searchParams.set('code', code)
    history.replaceState(null, '', url.toString())
    return () => { alive = false }
  }, [code])

  const loadAI = useCallback(() => {
    if (!code) return
    setAiLoading(true); setAiErr(null)
    api.interpret(code)
      .then(r => setAi(r))
      .catch(e => setAiErr(String(e.message || e)))
      .finally(() => setAiLoading(false))
  }, [code])

  const stale = daysSince(health?.asof)

  // ---------- 后端不可达 ----------
  if (bootErr) {
    return (
      <div className="page">
        <div className="masthead">
          <div className="kicker">研究笔记</div>
          <h1>29 本书观点 · 个股买入决策</h1>
        </div>
        <div className="err">无法连接后端：{bootErr}</div>
        <pre style={{ fontSize: 12.5, marginTop: 16 }}>
{`cd automation_stock_analyse
python -m uvicorn app.main:app --port 8000`}
        </pre>
      </div>
    )
  }

  // ---------- 快照未就绪 ----------
  if (health && !health.snapshot_ready) {
    return (
      <div className="page">
        <div className="masthead">
          <div className="kicker">研究笔记</div>
          <h1>29 本书观点 · 个股买入决策</h1>
          <div className="sub">
            核心分的分位与横截面分位数必须对全市场计算，所以运行时只查表、不重算。
          </div>
        </div>
        <pre style={{ fontSize: 12.5, background: 'var(--paper-2)', padding: 14 }}>
{`python -m app.build_snapshot`}
        </pre>
        <div className="small" style={{ marginTop: 12 }}>{health.hint}</div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="masthead">
        <div className="kicker">研究笔记</div>
        <h1>29 本书观点 · 个股买入决策</h1>
        <div className="sub">
          输入 A 股代码，看 29 本投资书对这只股票的逐本观点，以及一个由确定性规则给出的判定。
          {health && <> 　AI {health.ai_available ? `可用（${health.ai_model}）` : '不可用，将退化为纯规则报告'}。</>}
        </div>

        {stale !== null && (
          <div className={`stale ${stale > 30 ? 'bad' : stale > 7 ? 'warn' : ''}`}>
            <div>
              数据基准日 <strong>{health?.asof}</strong>，距今 <strong>{stale}</strong> 天
              {stale > 30
                ? ' — 已严重过期，分数与判定不应再用于实盘参考'
                : stale > 7
                  ? ' — 建议重建快照'
                  : ' — 离线快照，非实时行情'}
            </div>
            {stale > 7 && (
              <div className="howto">
                刷新：<code>python -m app.build_snapshot</code>（全市场约 2.5 分钟）
              </div>
            )}
          </div>
        )}

        <SearchBar onPick={setCode} />

        <div className="legend">
          <span><i className="solid" />事实层 · 已回测验证</span>
          <span><i className="dashed" />AI 批注 · 未经回测验证（默认折叠）</span>
        </div>
      </div>

      {loadingA && <div className="skel">正在计算…</div>}
      {aErr && <div className="err">{aErr}</div>}

      {a && (
        <>
          <Section n="01" title="判定" {...FACT}>
            <Verdict a={a} />
          </Section>

          {a.history && (
            <Section n="02" title="它相对自己的历史在哪" {...FACT}
              lede="单个分数回答不了这个问题。轨迹用回测面板的 77 期月度快照还原，分位逐期重算。">
              <HistoryChart h={a.history} />
            </Section>
          )}

          <Section n="03" title="这套分数把它排在哪一档" {...FACT}
            lede="把全市场按核心分五等分，看各组的「未来 60 日跌超 20%」比例。">
            <EvidencePanel ev={meta?.evidence || null} mine={a.badrate} />
          </Section>

          <Section n="04" title="越极端的灾难，越能分辨" {...FACT}
            lede="同一套分数，在三种「坏」的定义下的表现。这是它该被当作避雷工具而非收益策略的依据。">
            <ThresholdPanel thresholds={meta?.thresholds || []} />
          </Section>

          <Section n="05" title="维度分解" {...FACT}
            lede="29 个数字人是读不了的。归到 9 个语义簇，才看得出强在哪、弱在哪。">
            <ClusterPanel clusters={a.clusters || []} />
          </Section>

          <Section n="06" title="逐本观点" {...FACT}>
            <BooksPanel a={a} />
          </Section>

          <Section n="07" title="AI 批注" layer="ai"
            tag="未经回测验证" tagSub={<span>批注，<br />不改变判定</span>}>
            <AIPanel data={ai} loading={aiLoading} error={aiErr} onFirstOpen={loadAI} />
          </Section>

          <Section n="08" title="原始材料" {...FACT}
            lede="公告与研报的原文索引。上面那段批注就是从这些材料里读出来的。">
            <EventsPanel code={a.code} />
          </Section>

          <Section n="09" title="这份笔记的局限" {...FACT}
            lede="必须随结论一起读。">
            <Disclaimers items={a.disclaimers} />
          </Section>

          <div className="foot">
            scorer {health?.scorer_sha256} · panel {health?.panel_sha256} · v{health?.version}
          </div>
        </>
      )}

      {!a && !loadingA && !aErr && (
        <div className="small">
          {meta
            ? <>共 {meta.n_scored} 只可算股票。判定分布：{Object.entries(meta.band_distribution || {}).map(([k, v]) => `${k} ${v}`).join(' / ')}。</>
            : '加载中…'}
        </div>
      )}
    </div>
  )
}
