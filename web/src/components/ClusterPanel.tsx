import type { ClusterScore } from '../types'

/**
 * 把 29 个数字归到 9 个语义簇。
 *
 * 29 个分数人是读不了的；归簇之后才看得出「这只股票在哪些维度强、哪些弱」。
 * 竖线 = 全市场中位，条 = 该股在该簇的均分。
 */
export default function ClusterPanel({ clusters }: { clusters: ClusterScore[] }) {
  const rows = clusters.filter(c => c.score != null)
  if (!rows.length) return null

  return (
    <div className="layer layer-fact">
      <h2>维度分解 · 事实层<span className="tag">已回测验证</span></h2>
      <div className="small" style={{ marginBottom: 14 }}>
        29 本书归为 9 个语义簇。竖线是全市场中位；★ 表示该簇含有进入判定的核心书。
      </div>

      {rows.map(c => {
        const v = c.score as number
        const med = c.universe_median
        const d = c.diff
        const pos = d != null && d >= 0
        return (
          <div className="cluster" key={c.cluster}>
            <div className="hd">
              <span className="lb">
                {c.label}
                {c.has_core && <span className="cr">★ 含核心书</span>}
              </span>
              <span className="vl">
                {v}
                {med != null && <span className="small"> / 中位 {med}</span>}
                {d != null && (
                  <span style={{ color: pos ? 'var(--fact-2)' : 'var(--ai)', marginLeft: 6 }}>
                    {pos ? '+' : ''}{d}
                  </span>
                )}
              </span>
            </div>
            <div className="ds">{c.desc} · {c.n_available}/{c.n_books} 本可算</div>
            <div className="track2">
              <i
                className={pos ? 'pos' : 'neg'}
                style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }}
              />
              {med != null && <span className="med" style={{ left: `${med}%` }} />}
            </div>
          </div>
        )
      })}

      <div className="small" style={{ marginTop: 10 }}>
        簇内取等权均分，仅用可算的书（N/A 不计入）。簇只用于**展示**，不参与判定 ——
        判定只由核心 4 本等权得出。
      </div>
    </div>
  )
}
