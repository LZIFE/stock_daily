import type { ClusterScore } from '../types'

/**
 * 把 29 个数字归到 9 个语义簇。
 * 29 个分数人是读不了的；归簇之后才看得出「这只股票在哪些维度强、哪些弱」。
 *
 * 画法：上细线 = 该股在此簇的均分，刻度点 = 全市场中位。
 * 线长差 = 相对全市场的位置。
 */
export default function ClusterPanel({ clusters }: { clusters: ClusterScore[] }) {
  const rows = clusters.filter(c => c.score != null)
  if (!rows.length) return null

  return (
    <>
      {rows.map(c => {
        const v = c.score as number
        const med = c.universe_median
        const d = c.diff
        const pos = d != null && d >= 0
        return (
          <div className="dim" key={c.cluster}>
            <div className="hd">
              <span className="lb">
                {c.label}
                {c.has_core && <span className="cr">★ 含核心书</span>}
              </span>
              <span className="vl">
                {v}
                {med != null && <span className="small"> / 中位 {med}</span>}
                {d != null && (
                  <span style={{ color: pos ? 'var(--buy)' : 'var(--vermil)', marginLeft: 8 }}>
                    {pos ? '+' : ''}{d}
                  </span>
                )}
              </span>
            </div>
            <div className="ds">{c.desc} · {c.n_available}/{c.n_books} 本可算</div>
            <div className="rail">
              <span
                className={`fill${pos ? '' : ' neg'}`}
                style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }}
              />
              {med != null && <span className="med" style={{ left: `${med}%` }} />}
            </div>
          </div>
        )
      })}

      <div className="small" style={{ marginTop: 14 }}>
        簇内取等权均分，只用可算的书（N/A 不计入）。
        簇仅用于<strong>展示</strong>，不参与判定 —— 判定只由核心 4 本等权得出。
      </div>
    </>
  )
}
