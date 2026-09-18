import type { Evidence, BadRate } from '../types'

export default function EvidencePanel({ ev, mine }: { ev: Evidence | null; mine: BadRate | null }) {
  if (!ev) return null
  const qs = ev.quintiles || []
  const max = Math.max(...qs, 1)
  // 该股落在哪个五等分由后端给出（Q1 最低分 → Q5 最高分）
  let me = -1
  if (mine?.quintile && /^Q(\d)$/.test(mine.quintile)) me = +mine.quintile[1] - 1

  return (
    <>
      <div className="qbars">
        {qs.map((v, i) => (
          <div key={i} className={i === me ? 'me' : ''}>
            <i style={{ height: `${Math.max((v / max) * 70, 2)}px` }} />
            <div className="nm">{v.toFixed(1)}%</div>
            <div className="lab">Q{i + 1}{i === 0 ? ' 低分' : i === qs.length - 1 ? ' 高分' : ''}</div>
          </div>
        ))}
      </div>

      <div className="small" style={{ marginTop: 10 }}>
        把全市场按核心分五等分，各组的「未来 60 日跌超 20%」比例。
        窗口 {ev.window}，n={ev.n.toLocaleString()}，基准坏率 {ev.base_bad_rate}%，AUC {ev.auc}。
        {me >= 0 && <> 该股落在 <strong>{mine?.quintile}</strong>，坏率 {mine?.quintile_bad_rate}%。</>}
      </div>

      <div className="note ink" style={{ marginTop: 18 }}>
        股票池不含已退市股票，所以这些坏率是<strong>下界</strong>；
        未做行业/市值中性化，高分集中在低估值红利。这两个折扣请一并计入。
      </div>
    </>
  )
}
