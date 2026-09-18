import type { Threshold } from '../types'

/**
 * 多阈值坏率 —— 这套系统最值得展示的性质。
 *
 * 实测：跌超 10% 时高分组的坏率是低分组的 1/2.14，跌超 20% 是 1/4.28，
 * 跌超 30% 是 1/8.45（AUC 0.60 → 0.65 → 0.70）。
 * **越极端的灾难，核心分越能分辨** —— 这正好解释了它为什么不是收益策略，
 * 而是避雷工具：收益维度没证据，尾部风险维度证据很强。
 *
 * 条形画法：每行总宽 = 该阈值的 Q1 坏率，内部深色段 = Q5 坏率。
 * 所以深色段越短 = 区分度越强，且各行之间可比（因为按行归一）。
 */
export default function ThresholdPanel({ thresholds }: { thresholds: Threshold[] }) {
  const rows = (thresholds || []).slice().sort((a, b) => a.base_bad_rate - b.base_bad_rate)
  if (!rows.length) return null

  return (
    <div className="layer layer-fact">
      <h2>越极端的灾难，越能分辨 · 事实层<span className="tag">已回测验证</span></h2>
      <div className="small" style={{ marginBottom: 16 }}>
        同一套核心分，在三种「坏」的定义下的表现。深色段 = 高分位组（Q5）的坏率，
        浅色段 = 低分位组（Q1）。<strong>深色越短，说明高分越能避开这种灾难。</strong>
      </div>

      <div className="thr">
        {rows.map(t => {
          const inner = t.q1 > 0 ? (t.q5 / t.q1) * 100 : 0
          return (
            <div className="thr-row" key={t.label}>
              <div className="lb">
                {t.label}
                <span className="bs">基准 {t.base_bad_rate}%</span>
              </div>
              <div className="thr-bar" title={`Q1（最差组）${t.q1}%  →  Q5（最好组）${t.q5}%`}>
                <i className="q1" style={{ width: '100%' }} />
                <i className="q5" style={{ width: `${inner}%` }} />
              </div>
              <div className="rt">
                {t.ratio}x
                <span className="bs">{t.q1}% → {t.q5}%</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="hist-stats">
        {rows.map(t => (
          <div key={t.label}>
            <div className="k">{t.label} · AUC</div>
            <div className="v">{t.auc}</div>
          </div>
        ))}
      </div>

      <div className="small" style={{ marginTop: 12 }}>
        窗口：2022-03 ~ 2026-07 纯样本外，未来 60 日绝对收益。
        倍数单调放大（{rows.map(t => t.ratio + 'x').join(' → ')}）——
        这正是把产品定位成「避免踩雷的筛选器」而不是收益策略的依据：
        它在**极端亏损**上最强，在收益上没有证据。
      </div>
    </div>
  )
}
