import type { Threshold } from '../types'

/**
 * 多阈值坏率 —— 这套系统最值得展示的性质。
 *
 * 实测：跌超 10% 时高分组的坏率是低分组的 1/2.14，跌超 20% 是 1/4.28，
 * 跌超 30% 是 1/8.45（AUC 0.60 → 0.65 → 0.70）。
 * **越极端的灾难，核心分越能分辨** —— 这正是它该被当作避雷工具而非收益策略的理由。
 *
 * 画法：上细线 = Q1（最差组）坏率，下粗线 = Q5（最好组）坏率，同起点。
 * 两条线的长度差 = 区分度。用线而不是填充条，是为了让「长度」这件事看得更准。
 */
export default function ThresholdPanel({ thresholds }: { thresholds: Threshold[] }) {
  const rows = (thresholds || []).slice().sort((a, b) => a.base_bad_rate - b.base_bad_rate)
  if (!rows.length) return null

  return (
    <>
      {rows.map(t => {
        const inner = t.q1 > 0 ? (t.q5 / t.q1) * 100 : 0
        return (
          <div className="thr-row" key={t.label}>
            <div className="lb">
              {t.label}
              <span className="bs">基准 {t.base_bad_rate}%</span>
            </div>
            <div className="thr-rail" title={`Q1（最差组）${t.q1}%　Q5（最好组）${t.q5}%`}>
              <span className="base" />
              <span className="q1" style={{ width: '100%' }} />
              <span className="q5" style={{ width: `${inner}%` }} />
            </div>
            <div className="rt">
              {t.ratio}x
              <span className="bs">{t.q1}% → {t.q5}%</span>
            </div>
          </div>
        )
      })}

      <div className="hist-stats">
        {rows.map(t => (
          <div key={t.label}>
            <div className="k">{t.label} · AUC</div>
            <div className="v">{t.auc}</div>
          </div>
        ))}
      </div>

      <div className="note" style={{ marginTop: 18 }}>
        倍数单调放大（{rows.map(t => t.ratio + 'x').join(' → ')}）——
        这就是把产品定位成「避免踩雷的筛选器」而不是收益策略的依据：
        它在<strong>极端亏损</strong>上最强，在收益上没有证据。
      </div>
    </>
  )
}
