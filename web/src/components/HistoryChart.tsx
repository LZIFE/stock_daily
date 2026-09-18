import type { HistoryOut } from '../types'

/**
 * 核心分历史轨迹。
 *
 * 单个分数回答不了「现在的情况」里的关键问题：相对它自己的历史，这是高还是低。
 *
 * 诚实性细节：
 *  · 分位**逐期重算**（用当期横截面），不是拿今天的分位回看历史
 *  · 点的颜色按**当期**判定 —— 拿今天的阈值套到过去会犯「用未来信息」的错
 *  · 末点来自当前快照（面板只到 2026-07-31），用空心点区分
 *
 * 实现注意：SVG 用 preserveAspectRatio="none" 横向铺满，**所有文字必须放在 SVG 外面**
 * —— 否则会被横向拉伸变形（这是首版轴标签糊掉的原因）。
 */
export default function HistoryChart({ h }: { h: HistoryOut }) {
  const pts = h.points
  if (!pts || pts.length < 3) return null

  const W = 900, H = 120, PL = 2, PR = 2, PT = 10, PB = 6
  const xs = (i: number) => PL + (i / (pts.length - 1)) * (W - PL - PR)
  // y 轴必须贴合数据实际区间。固定成 30~80 会把多数股票压成一条平线。
  const lo = h.min, hi = h.max
  const pad = Math.max((hi - lo) * 0.18, 1.5)
  const y0 = lo - pad, y1 = hi + pad
  const ys = (v: number) => PT + (1 - (v - y0) / (y1 - y0)) * (H - PT - PB)

  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${xs(i).toFixed(1)},${ys(p.core_score).toFixed(1)}`).join(' ')
  const area = `${line} L${xs(pts.length - 1).toFixed(1)},${H} L${xs(0).toFixed(1)},${H} Z`

  const sorted = pts.map(p => p.core_score).slice().sort((x, y) => x - y)
  const medScore = sorted[Math.floor(sorted.length / 2)]

  const bandOf = (p: number) => (p >= 90 ? 'BUY' : p >= 70 ? 'WATCH' : 'AVOID')
  const cls = (b: string) => (b === 'BUY' ? 'pt-buy' : b === 'WATCH' ? 'pt-watch' : 'pt')

  const n = pts.length
  const tickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1]

  return (
    <>
      <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        <path className="ar" d={area} />
        {/* 历史中位参考线：一眼看出「现在高于还是低于自己的常态」 */}
        <line
          className="bandline"
          x1={0} x2={W} y1={ys(medScore)} y2={ys(medScore)}
          vectorEffect="non-scaling-stroke"
        />
        <path className="ln" d={line} vectorEffect="non-scaling-stroke" />
        {pts.map((p, i) => {
          if (n > 60 && i % 2 === 1) return null
          const last = i === n - 1
          return (
            <circle
              key={i}
              cx={xs(i)} cy={ys(p.core_score)} r={last ? 4 : 2.6}
              className={last ? 'pt-now' : cls(bandOf(p.pctl))}
              vectorEffect="non-scaling-stroke"
            >
              <title>{`${p.date}　核心分 ${p.core_score}　分位 ${p.pctl}　→ ${bandOf(p.pctl)}`}</title>
            </circle>
          )
        })}
      </svg>

      {/* 轴标签用 HTML 渲染，避免 SVG 横向拉伸把字压扁 */}
      <div className="spark-x">
        {tickIdx.map((i, k) => (
          <span
            key={k}
            style={{
              textAlign: k === 0 ? 'left' : k === tickIdx.length - 1 ? 'right' : 'center',
            }}
          >
            {pts[i].date.slice(0, 7)}
          </span>
        ))}
      </div>

      <div className="hist-stats">
        <div><div className="k">当前</div><div className="v">{pts[n - 1].core_score}</div></div>
        <div><div className="k">历史区间</div><div className="v">{h.min}–{h.max}</div></div>
        <div>
          <div className="k">首末变化</div>
          <div className="v" style={{ color: h.delta >= 0 ? 'var(--buy)' : 'var(--vermil)' }}>
            {h.delta >= 0 ? '+' : ''}{h.delta}
          </div>
        </div>
        <div><div className="k">当前分位</div><div className="v">{h.pctl_now}</div></div>
        <div><div className="k">历史分位中位</div><div className="v">{h.pctl_median}</div></div>
        <div><div className="k">样本期数</div><div className="v">{h.n}</div></div>
      </div>

      <div className="small" style={{ marginTop: 12 }}>
        虚线 = 历史中位 {medScore}。点色 = 当期判定
        （<span style={{ color: 'var(--buy)' }}>●</span> BUY
        {' / '}<span style={{ color: 'var(--watch)' }}>●</span> WATCH
        {' / '}<span style={{ color: 'var(--ink-3)' }}>●</span> AVOID）。
        分位逐期重算，不是用今天的分位回看历史；末点为当前快照（面板只到 2026-07-31）。
      </div>
    </>
  )
}
