import { useEffect, useState } from 'react'
import { screenApi } from '../api'
import type { ScreenKind, ScreenOut } from '../types'

/**
 * 全市场榜单。
 *
 * 命名与呈现的诚实性（决定用户怎么用它）：
 *  · 叫「低踩雷概率」而不是「推荐买入」
 *  · 每条都带并列只数与该桶历史坏率
 *  · 并列极多，必须显示 tiebreak 说明 —— 否则「第一名」会被当真
 */
export default function Screening({ onPick }: { onPick: (code: string) => void }) {
  const [kinds, setKinds] = useState<ScreenKind[]>([])
  const [kind, setKind] = useState('low_risk')
  const [data, setData] = useState<ScreenOut | null>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    screenApi.kinds().then(setKinds).catch(() => {})
  }, [])

  useEffect(() => {
    let alive = true
    setLoading(true); setErr(null)
    screenApi.screen(kind, 30)
      .then(r => alive && setData(r))
      .catch(e => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [kind])

  return (
    <>
      <div className="tabs">
        {kinds.map(k => (
          <button
            key={k.kind}
            className={`tab${k.kind === kind ? ' on' : ''}`}
            onClick={() => setKind(k.kind)}
            title={k.lede}
          >
            {k.title}
          </button>
        ))}
      </div>

      {data && (
        <div className="small" style={{ marginBottom: 14 }}>
          {data.meta.lede}
        </div>
      )}

      {loading && <div className="skel">正在排序…</div>}
      {err && <div className="err">{err}</div>}

      {data && !loading && (
        <>
          <table>
            <thead>
              <tr>
                <th style={{ width: 88 }}>代码</th>
                <th style={{ width: 92 }}>名称</th>
                <th style={{ width: 58 }}>判定</th>
                <th className="num" style={{ width: 52 }}>核心分</th>
                <th className="num" style={{ width: 56 }}>分位</th>
                <th className="num" style={{ width: 52 }}>并列</th>
                <th className="num" style={{ width: 58 }}>分歧</th>
                <th className="num" style={{ width: 62 }}>近3期</th>
                <th className="num" style={{ width: 60 }}>该桶坏率</th>
                <th>行业</th>
              </tr>
            </thead>
            <tbody>
              {data.rows.map(r => (
                <tr
                  key={r.code}
                  onClick={() => onPick(r.code)}
                  style={{ cursor: 'pointer' }}
                  title={`${r.code} ${r.name} —— 点击查看完整分析`}
                >
                  <td className="num" style={{ textAlign: 'left' }}>{r.code}</td>
                  <td>{r.name}</td>
                  <td>
                    <span style={{
                      color: r.band === 'BUY' ? 'var(--buy)'
                        : r.band === 'WATCH' ? 'var(--watch)' : 'var(--ink-3)',
                    }}>{r.band}</span>
                  </td>
                  <td className="num">{r.core_score}</td>
                  <td className="num">{r.core_pctl}</td>
                  <td className="num small">{r.n_tied}</td>
                  <td className="num">{r.divergence != null
                    ? (r.divergence > 0 ? '+' : '') + r.divergence : '—'}</td>
                  <td className="num" style={{
                    color: (r.delta3 ?? 0) > 0 ? 'var(--buy)' : (r.delta3 ?? 0) < 0 ? 'var(--vermil)' : undefined,
                  }}>{r.delta3 != null ? (r.delta3 > 0 ? '+' : '') + r.delta3 : '—'}</td>
                  <td className="num">{r.badrate?.bad_rate ?? '—'}%</td>
                  <td className="small">
                    {r.industries.slice(0, 2).join(' / ') || '—'}
                    {!r.pe_available && <span className="unv" style={{ marginLeft: 6 }}>无 PE</span>}
                    {r.flags.includes('流动性受限') && <span className="unv" style={{ marginLeft: 6 }}>低流动</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="small" style={{ marginTop: 12 }}>
            {data.meta.tiebreak_note}
          </div>
          <div className="note" style={{ marginTop: 14 }}>
            {data.disclaimer}
          </div>
          <div className="small" style={{ marginTop: 10 }}>
            共 {data.meta.n_universe} 只可算股票，此处显示前 {data.meta.n_returned} 只。
            {data.meta.industry_coverage_note} 点击任意一行查看完整分析。
          </div>
        </>
      )}
    </>
  )
}
