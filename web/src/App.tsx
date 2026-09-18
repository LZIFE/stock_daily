import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import type { Analysis, HealthOut, Interpretation, SnapshotMeta } from './types'
import SearchBar from './components/SearchBar'
import VerdictCard from './components/VerdictCard'
import BooksPanel from './components/BooksPanel'
import EvidencePanel from './components/EvidencePanel'
import AIPanel from './components/AIPanel'
import EventsPanel from './components/EventsPanel'
import Disclaimers from './components/Disclaimers'

function initialCode(): string {
  return new URLSearchParams(location.search).get('code') || ''
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

  // ---------- 快照未就绪 ----------
  if (bootErr) {
    return (
      <div className="wrap">
        <h1>29 本书观点 · 个股买入决策</h1>
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

  if (health && !health.snapshot_ready) {
    return (
      <div className="wrap">
        <h1>29 本书观点 · 个股买入决策</h1>
        <div className="card">
          <h2>需要先构建快照</h2>
          <div style={{ fontSize: 13.5 }}>
            核心分的分位与横截面分位数必须对全市场计算，所以运行时只查表、不重算。
          </div>
          <pre style={{ fontSize: 12.5, background: '#f6f7f9', padding: 12, borderRadius: 8 }}>
{`python -m app.build_snapshot`}
          </pre>
          <div className="small">{health.hint}</div>
        </div>
      </div>
    )
  }

  // ---------- 主界面 ----------
  return (
    <div className="wrap">
      <h1>29 本书观点 · 个股买入决策</h1>
      <div className="sub">
        输入 A 股代码，看 29 本投资书对这只股票的逐本观点，以及一个由确定性规则给出的判定。
        {health?.asof && <> 数据基准日 <strong>{health.asof}</strong>（离线快照，非实时）。</>}
        {health && <> AI {health.ai_available ? `可用（${health.ai_model}）` : '不可用，将退化为纯规则报告'}。</>}
      </div>

      <div className="legend">
        <span><i style={{ borderTopColor: 'var(--fact)', borderTopStyle: 'solid' }} />事实层 · 已回测验证</span>
        <span><i style={{ borderTopColor: 'var(--ai)', borderTopStyle: 'dashed' }} />AI 解读 · 未经回测验证</span>
      </div>

      <div style={{ marginBottom: 16 }}>
        <SearchBar onPick={setCode} />
      </div>

      {loadingA && <div className="skel">加载中…</div>}
      {aErr && <div className="card err">{aErr}</div>}

      {a && (
        <>
          <VerdictCard a={a} />
          <EvidencePanel ev={meta?.evidence || null} mine={a.badrate} />
          <BooksPanel a={a} />
          <AIPanel data={ai} loading={aiLoading} error={aiErr} onFirstOpen={loadAI} />
          <EventsPanel code={a.code} />
          <Disclaimers items={a.disclaimers} />

          <div className="small" style={{ marginTop: 10 }}>
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
