import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import type { Analysis, HealthOut, Interpretation, SnapshotMeta } from './types'
import SearchBar from './components/SearchBar'
import Hero from './components/Hero'
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
 * 刻意做分级告警：这套分数会随快照老化而失效，而界面上每个数字看起来都一样「新鲜」，
 * 不提醒的话用户很容易拿三个月前的判定当今天的用。
 */
function daysSince(d?: string | null): number | null {
  if (!d) return null
  const t = new Date(d + 'T00:00:00').getTime()
  if (Number.isNaN(t)) return null
  return Math.floor((Date.now() - t) / 86400000)
}

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
      <div className="wrap">
        <div className="masthead">
          <h1>29 本书观点 · 个股买入决策</h1>
        </div>
        <div className="card err">无法连接后端：{bootErr}</div>
        <div className="card">
          <h2>启动方式</h2>
          <pre style={{ fontSize: 12.5, margin: 0 }}>
{`cd automation_stock_analyse
python -m uvicorn app.main:app --port 8000`}
          </pre>
        </div>
      </div>
    )
  }

  // ---------- 快照未就绪 ----------
  if (health && !health.snapshot_ready) {
    return (
      <div className="wrap">
        <div className="masthead">
          <h1>29 本书观点 · 个股买入决策</h1>
        </div>
        <div className="card">
          <h2>需要先构建快照</h2>
          <div style={{ fontSize: 13.5 }}>
            核心分的分位与横截面分位数必须对全市场计算，所以运行时只查表、不重算。
          </div>
          <pre style={{ fontSize: 12.5, background: 'var(--bg-2)', padding: 12, borderRadius: 8 }}>
{`python -m app.build_snapshot`}
          </pre>
          <div className="small">{health.hint}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="wrap">
      <div className="masthead">
        <h1>29 本书观点 · 个股买入决策</h1>
        <div className="sub">
          输入 A 股代码，看 29 本投资书对这只股票的逐本观点，以及一个由确定性规则给出的判定。
          {health && <> AI {health.ai_available ? `可用（${health.ai_model}）` : '不可用，将退化为纯规则报告'}。</>}
        </div>
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

      <div className="legend">
        <span><i style={{ borderTopColor: 'var(--fact)', borderTopStyle: 'solid' }} />事实层 · 已回测验证</span>
        <span><i style={{ borderTopColor: 'var(--ai)', borderTopStyle: 'dashed' }} />AI 解读 · 未经回测验证（默认折叠）</span>
      </div>

      <div style={{ marginBottom: 18 }}>
        <SearchBar onPick={setCode} />
      </div>

      {loadingA && <div className="skel">正在计算…</div>}
      {aErr && <div className="card err">{aErr}</div>}

      {a && (
        <>
          <Hero a={a} />
          {a.history && <HistoryChart h={a.history} />}
          <EvidencePanel ev={meta?.evidence || null} mine={a.badrate} />
          <ThresholdPanel thresholds={meta?.thresholds || []} />
          <ClusterPanel clusters={a.clusters || []} />
          <BooksPanel a={a} />
          <AIPanel data={ai} loading={aiLoading} error={aiErr} onFirstOpen={loadAI} />
          <EventsPanel code={a.code} />
          <Disclaimers items={a.disclaimers} />

          <div className="foot">
            scorer {health?.scorer_sha256} · panel {health?.panel_sha256} · v{health?.version}
          </div>
        </>
      )}

      {!a && !loadingA && !aErr && (
        <div className="card small">
          {meta
            ? <>共 {meta.n_scored} 只可算股票。判定分布：{Object.entries(meta.band_distribution || {}).map(([k, v]) => `${k} ${v}`).join(' / ')}。</>
            : '加载中…'}
        </div>
      )}
    </div>
  )
}
