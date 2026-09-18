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
    <div className="card">
      <h2>公告与研报 · 原始材料</h2>
      {loading && <div className="skel">加载中…</div>}
      {err && <div className="err">抓取失败：{err}</div>}

      {!!ann.length && (
        <>
          <div className="zone">最近公告（{ann.length} 条）</div>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {ann.slice(0, 10).map((a, i) => (
              <li key={i} style={{ fontSize: 13, marginBottom: 4 }}>
                <span className="small">{a.notice_date}</span>{' '}
                {a.title.replace(/^[^:]*:/, '')}
                {!!a.columns.length && (
                  <span className="chip" style={{ marginLeft: 6 }}>{a.columns.join('/')}</span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}

      <div className="zone" style={{ marginTop: 14 }}>
        券商研报（近半年）
        {!!Object.keys(dist).length && (
          <span className="small"> · 评级分布：{Object.entries(dist).map(([k, v]) => `${k} ${v}`).join(' / ')}</span>
        )}
      </div>
      {note && <div className="small">{note}</div>}
      {!!rep.length && (
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {rep.slice(0, 8).map((r, i) => (
            <li key={i} style={{ fontSize: 13, marginBottom: 4 }}>
              <span className="small">{r.publish_date}</span>{' '}
              <span className="chip">{r.rating || '无评级'}</span>{' '}
              {r.org} — {r.title}
            </li>
          ))}
        </ul>
      )}
      {!loading && !ann.length && !rep.length && !err && (
        <div className="small">未获取到公告或研报。</div>
      )}
      <div className="small" style={{ marginTop: 8 }}>
        公告正文接口上限 5000 字符。实测长公告（年报/半年报）的关键财务数据
        —— 营收、归母净利、经营现金流、净资产、总资产、EPS、加权 ROE ——
        都落在前 4000 字内，截断的是非经常性损益等附录细节。
      </div>
    </div>
  )
}
