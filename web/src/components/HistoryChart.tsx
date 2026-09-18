import type { HistoryOut } from '../types'

/**
 * 核心分历史轨迹。
 *
 * 为什么画它：单个分数（60.5）回答不了「现在的情况」里的关键问题 ——
 * 相对它自己的历史，这是高还是低。
 *
 * 诚实性细节：
 *  · 分位是**逐期重算**的（用当期横截面），不是拿今天的分位回看历史
 *  · 点的颜色按**当期** band 着色 —— 因为 band 由当期分位决定，
 *    直接拿今天的阈值套到过去会犯「用未来信息」的错
 *  · 最后一点来自当前快照（面板只到 2026-07-31），用空心点区分
 */
export default function HistoryChart({ h }: { h: HistoryOut }) {
  const pts = h.points
  if (!pts || pts.length < 3) return null

  const W = 900, H = 120, PL = 6, PR = 6, PT = 12, PB = 16
  const xs = (i: number) => PL + (i / (pts.length - 1)) * (W - PL - PR)
  const lo = Math.min(h.min, 30), hi = Math.max(h.max, 80)
  const pad = Math.max((hi - lo) * 0.14, 3)
  const y0 = lo - pad, y1 = hi + pad
  const ys = (v: number) => PT + (1 - (v - y0) / (y1 - y0)) * (H - PT - PB)

  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${xs(i).toFixed(1)},${ys(p.core_score).toFixed(1)}`).join(' ')
  const area = `${line} L${xs(pts.length - 1).toFixed(1)},${H - PB} L${xs(0).toFixed(1)},${H - PB} Z`

  const bandOf = (p: number) => (p >= 90 ? 'BUY' : p >= 70 ? 'WATCH' : 'AVOID')
  const color = (b: string) =>
    b === 'BUY' ? '#14805a' : b === 'WATCH' ? '#b07407' : '#a3aec0'

  const n = pts.length
  const ticks = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1]

  return (
    <div className="layer layer-fact">
      <h2>
        核心分的历史轨迹 · 事实层
        <span className="tag">已回测验证</span>
      </h2>

      <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="gspark" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0d8b8d" stopOpacity="1" />
            <stop offset="100%" stopColor="#0d8b8d" stopOpacity="0" />
          </linearGradient>
        </defs>

        <path className="ar" d={area} />
        <path className="ln" d={line} vectorEffect="non-scaling-stroke" />

        {/* 每个点按当期 band 着色；点数多时只画后段 */}
        {pts.map((p, i) => {
          if (n > 60 && i % 2 === 1) return null
          const b = bandOf(p.pctl)
          const last = i === n - 1
          return (
            <circle
              key={i}
              cx={xs(i)} cy={ys(p.core_score)} r={last ? 4.5 : 3}
              fill={last ? '#fff' : color(b)}
              stroke={last ? '#0d8b8d' : 'none'}
              strokeWidth={last ? 2.5 : 0}
              vectorEffect="non-scaling-stroke"
            >
              <title>{`${p.date}  核心分 ${p.core_score}  分位 ${p.pctl}  → ${b}`}</title>
            </circle>
          )
        })}

        {/* x 轴刻度 */}
        {ticks.map((i, k) => (
          <text
            key={k}
            className="lbl"
            x={xs(i)}
            y={H - 4}
            textAnchor={k === 0 ? 'start' : k === ticks.length - 1 ? 'end' : 'middle'}
          >
            {pts[i].date.slice(0, 7)}
          </text>
        ))}
      </svg>

      <div className="hist-stats">
        <div>
          <div className="k">当前</div>
          <div className="v">{h.points[n - 1].core_score}</div>
        </div>
        <div>
          <div className="k">历史区间</div>
          <div className="v">{h.min}–{h.max}</div>
        </div>
        <div>
          <div className="k">首末变化</div>
          <div className="v" style={{ color: h.delta >= 0 ? 'var(--buy)' : 'var(--danger)' }}>
            {h.delta >= 0 ? '+' : ''}{h.delta}
          </div>
        </div>
        <div>
          <div className="k">当前分位</div>
          <div className="v">{h.pctl_now}</div>
        </div>
        <div>
          <div className="k">历史分位中位</div>
          <div className="v">{h.pctl_median}</div>
        </div>
        <div>
          <div className="k">样本期数</div>
          <div className="v">{h.n}</div>
        </div>
      </div>

      <div className="small" style={{ marginTop: 10 }}>
        点色 = 当期判定（<span style={{ color: '#14805a' }}>●</span> BUY
        {' / '}<span style={{ color: '#b07407' }}>●</span> WATCH
        {' / '}<span style={{ color: '#a3aec0' }}>●</span> AVOID）。
        分位逐期重算，不是用今天的分位回看历史；末点为当前快照（面板只到 2026-07-31）。
      </div>
    </div>
  )
}
