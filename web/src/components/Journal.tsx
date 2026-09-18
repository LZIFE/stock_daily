import { useCallback, useEffect, useState } from 'react'
import { journalApi } from '../api'
import type { JournalEntry, JournalOut } from '../types'

/**
 * 决策日志 + 自动复盘。
 *
 * **这是唯一能让你自己验证系统准不准的功能。**
 *
 * 关键：复盘按**系统自己的承诺**打分（60 日内是否跌超 20%），**不按收益率**。
 * 收益维度实测无证据，拿它当成败判据等于把没证据的东西包装成有证据。
 */
export default function Journal({
  onPick, refreshKey = 0, initialCode = '',
}: {
  onPick: (code: string) => void
  refreshKey?: number
  /** 从个股页面过来时预填代码，少一次输入 */
  initialCode?: string
}) {
  const [data, setData] = useState<JournalOut | null>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [code, setCode] = useState('')
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true); setErr(null)
    journalApi.list()
      .then(setData)
      .catch(e => setErr(String(e.message || e)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load, refreshKey])
  useEffect(() => { if (initialCode) setCode(initialCode) }, [initialCode])

  const submit = async () => {
    if (!code.trim()) return
    setBusy(true); setMsg(null)
    try {
      await journalApi.add(code.trim(), note.trim())
      setCode(''); setNote('')
      setMsg('已记录。判定与分数在入场时冻结，之后不可改 —— 否则复盘会自欺。')
      load()
    } catch (e: any) {
      setMsg(`记录失败：${e.message || e}`)
    } finally {
      setBusy(false)
    }
  }

  const del = async (id: string) => {
    try { await journalApi.remove(id); load() } catch { /* ignore */ }
  }

  const s = data?.summary

  return (
    <>
      <div className="jform">
        <input
          value={code} placeholder="股票代码，如 600519"
          aria-label="要记录的股票代码"
          onChange={e => setCode(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
        />
        <input
          value={note} placeholder="为什么记它（可留空）"
          aria-label="记录说明"
          onChange={e => setNote(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
        />
        <button className="btn" onClick={submit} disabled={busy || !code.trim()}>
          {busy ? '记录中…' : '记入日志'}
        </button>
      </div>

      {msg && <div className="small" style={{ marginTop: 8 }}>{msg}</div>}
      {loading && <div className="skel">加载日志…</div>}
      {err && <div className="err">{err}</div>}

      {s && s.n_total > 0 && (
        <div className="hist-stats" style={{ marginTop: 18 }}>
          <div>
            <div className="k">已记录</div>
            <div className="v">{s.n_total}</div>
          </div>
          <div>
            <div className="k">已满 {s.horizon_days} 日</div>
            <div className="v">{s.n_observed}</div>
          </div>
          <div>
            <div className="k">观察中</div>
            <div className="v">{s.n_pending}</div>
          </div>
          <div>
            <div className="k">实际踩雷率</div>
            <div className="v" style={{
              color: (s.observed_bad_rate ?? 0) > (s.expected_bad_rate_mean ?? 0)
                ? 'var(--danger)' : 'var(--buy)',
            }}>
              {s.observed_bad_rate != null ? `${s.observed_bad_rate}%` : '—'}
            </div>
          </div>
          <div>
            <div className="k">当时预期</div>
            <div className="v">{s.expected_bad_rate_mean != null ? `${s.expected_bad_rate_mean}%` : '—'}</div>
          </div>
          <div>
            <div className="k">全市场基准</div>
            <div className="v">{s.base_bad_rate != null ? `${s.base_bad_rate}%` : '—'}</div>
          </div>
        </div>
      )}

      {!!data?.entries.length && (
        <table style={{ marginTop: 18 }}>
          <thead>
            <tr>
              <th style={{ width: 84 }}>入场日</th>
              <th style={{ width: 92 }}>股票</th>
              <th style={{ width: 58 }}>当时</th>
              <th style={{ width: 58 }}>现在</th>
              <th className="num" style={{ width: 74 }}>最大回撤</th>
              <th style={{ width: 96 }}>60 日内</th>
              <th>备注</th>
              <th style={{ width: 34 }} />
            </tr>
          </thead>
          <tbody>
            {data.entries.map(e => {
              const v = e.verify
              const done = v.status === 'observed'
              return (
                <tr key={e.id}>
                  <td className="small">{e.date}</td>
                  <td>
                    <a
                      href={`?code=${e.code}`}
                      onClick={ev => { ev.preventDefault(); onPick(e.code) }}
                      style={{ color: 'var(--ink)', borderBottom: '1px solid var(--rule)' }}
                    >
                      {e.name || e.code}
                    </a>
                    <span className="small"> {e.code}</span>
                  </td>
                  <td style={{ color: 'var(--ink-2)' }}>{e.band_at_entry}</td>
                  <td style={{
                    color: e.band_changed ? 'var(--vermil)' : 'var(--ink-3)',
                  }}>
                    {e.band_now || '—'}{e.band_changed && ' *'}
                  </td>
                  <td className="num">
                    {done ? `${v.max_drawdown_pct}%` : `${v.progress ?? 0}%`}
                  </td>
                  <td>
                    {done
                      ? (v.hit_bad
                        ? <span style={{ color: 'var(--danger)' }}>跌超 20%（{v.hit_date}）</span>
                        : <span style={{ color: 'var(--buy)' }}>未跌超 20%</span>)
                      : <span className="small">观察中 {v.n_observed}/{v.horizon_days} 日</span>}
                  </td>
                  <td className="small">{e.note || '—'}</td>
                  <td>
                    <button
                      className="link" style={{ fontSize: 11 }}
                      onClick={() => del(e.id)}
                      aria-label={`删除 ${e.name || e.code} 的记录`}
                    >
                      删
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}

      {data && data.entries.length === 0 && !loading && (
        <div className="small" style={{ marginTop: 14 }}>
          还没有记录。在上方填入代码即可开始 —— 之后系统会自动按它自己的承诺
          （60 日内是否跌超 20%）复盘，而不是按收益率。
        </div>
      )}

      {s && (
        <div className="note ink" style={{ marginTop: 18 }}>
          {s.note}
          {s.n_observed > 0 && s.n_observed < 30 && (
            <> 目前只有 {s.n_observed} 条已满期样本 —— <strong>样本太少，还看不出任何东西</strong>，
            别急着下结论。</>
          )}
        </div>
      )}
    </>
  )
}
