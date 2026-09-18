import type { Evidence, BadRate } from '../types'

export default function EvidencePanel({ ev, mine }: { ev: Evidence | null; mine: BadRate | null }) {
  if (!ev) return null
  const qs = ev.quintiles || []
  const max = Math.max(...qs, 1)
  // 该股落在哪个五等分由后端 badrate.quintile 给出（Q1 最低分 → Q5 最高分）
  let me = -1
  if (mine?.quintile && /^Q(\d)$/.test(mine.quintile)) me = +mine.quintile[1] - 1

  return (
    <div className="layer layer-fact">
      <h2>这套分数的历史表现 · 事实层<span className="tag">已回测验证</span></h2>
      <div className="qbars">
        {qs.map((v, i) => (
          <div key={i} className={i === me ? 'me' : ''}>
            <i style={{ height: `${Math.max((v / max) * 62, 3)}px` }} />
            <div><span>{v.toFixed(1)}%</span></div>
            <div className="lab">Q{i + 1}{i === 0 ? ' 低分' : i === qs.length - 1 ? ' 高分' : ''}</div>
          </div>
        ))}
      </div>
      <div className="small" style={{ marginTop: 8 }}>
        未来 60 日绝对收益 &lt; −20% 的比例。窗口 {ev.window}，n={ev.n.toLocaleString()}，
        基准坏率 {ev.base_bad_rate}%，AUC {ev.auc}。
        {me >= 0 && <> 该股落在 <strong>{mine?.quintile}</strong>（坏率 {mine?.quintile_bad_rate}%）。</>}
      </div>
      <div className="small" style={{ marginTop: 6 }}>
        ⚠️ 股票池不含已退市股票，坏率是<strong>下界</strong>；未做行业/市值中性化，高分集中在低估值红利。
      </div>
    </div>
  )
}
