import { useEffect, useState } from 'react'
import { api } from '../api'
import type { AnnouncementItem, ReportItem } from '../types'

export default function EventsPanel({ code }: { code: string }) {
  const [ann, setAnn] = useState<AnnouncementItem[]>([])
  const [rep, setRep] = useState<ReportItem[]>([])
  const [dist, setDist] = useState<Record<string, number>>({})
  const [note, setNote] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    setLoading(true); setErr(null)
    Promise.all([api.announcements(code, 20), api.reports(code, 20)])
      .then(([a, r]) => {
        if (!alive) return
        setAnn(a.items || []); setRep(r.items || [])
        setDist(r.rating_distribution || {}); setNote(r.note || null)
        setErr(a.error || r.error || null)
      })
      .catch(e => alive && setErr(String(e.message || e)))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [code])

  return (
    <>
      {loading && <div className="skel">正在抓取公告与研报…</div>}
      {err && <div className="err">抓取失败：{err}</div>}

      {!!ann.length && (
        <>
          <div className="zone">最近公告<span className="hint">　{ann.length} 条</span></div>
          <table>
            <tbody>
              {ann.slice(0, 12).map((a, i) => (
                <tr key={i}>
                  <td style={{ width: 92 }} className="small">{a.notice_date}</td>
                  <td>{a.title.replace(/^[^:]*:/, '')}</td>
                  <td style={{ width: 132 }} className="small">
                    {a.columns.length ? a.columns.join('/') : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <div className="zone">
        券商研报<span className="hint">　近半年</span>
        {!!Object.keys(dist).length && (
          <span className="hint">
            　评级分布：{Object.entries(dist).map(([k, v]) => `${k} ${v}`).join(' / ')}
          </span>
        )}
      </div>
      {note && <div className="small">{note}</div>}
      {!!rep.length && (
        <table>
          <tbody>
            {rep.slice(0, 10).map((r, i) => (
              <tr key={i}>
                <td style={{ width: 92 }} className="small">{r.publish_date}</td>
                <td style={{ width: 66 }} className="small">{r.rating || '—'}</td>
                <td style={{ width: 96 }} className="small">{r.org}</td>
                <td>{r.title}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {!loading && !ann.length && !rep.length && !err && (
        <div className="small">未获取到公告或研报。</div>
      )}

      <div className="small" style={{ marginTop: 12 }}>
        公告正文接口上限 5000 字符。实测长公告（年报/半年报）的关键财务数据
        —— 营收、归母净利、经营现金流、净资产、总资产、EPS、加权 ROE ——
        都落在前 4000 字内，截断的是非经常性损益等附录细节。
      </div>
    </>
  )
}
