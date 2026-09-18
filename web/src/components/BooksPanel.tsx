import type { Analysis } from '../types'

export default function BooksPanel({ a }: { a: Analysis }) {
  const core = a.books.filter(b => b.core)
  const rest = a.books.filter(b => !b.core)

  return (
    <>
      <div className="zone">
        ★ 核心 4 本
        <span className="hint">
          　在分类目标上被 walk-forward 验证过（纯样本外 Q1 坏率 19.36% → Q5 4.52%，AUC 0.649）。
          只有这 4 本进入判定。
        </span>
      </div>
      <table>
        <thead>
          <tr>
            <th style={{ width: 104 }}>书</th>
            <th className="num" style={{ width: 54 }}>分数</th>
            <th>规则（以及触发它的数据）</th>
          </tr>
        </thead>
        <tbody>
          {core.map(b => (
            <tr key={b.name} className="core">
              <td><span className="star">★</span> {b.name}</td>
              <td className="num">
                {b.available ? b.score : <span title="算不出来，绝不是 50">N/A</span>}
              </td>
              <td className="rule-txt">{b.rule}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="zone">
        其余 25 本
        <span className="hint">
          　29 本等权共识在 walk-forward 上 AUC 0.5237（≈随机）、跨度仅 2.39pp。
          这些分数不进入判定，仅展示「其他作者怎么看」。
        </span>
      </div>
      <table>
        <thead>
          <tr>
            <th style={{ width: 104 }}>书</th>
            <th className="num" style={{ width: 54 }}>分数</th>
            <th style={{ width: 84 }}>簇</th>
            <th>规则</th>
          </tr>
        </thead>
        <tbody>
          {rest.map(b => (
            <tr key={b.name} className={b.available ? '' : 'unavail'}>
              <td>{b.name}</td>
              <td className="num">{b.available ? b.score : <span title="算不出来">N/A</span>}</td>
              <td className="small">{b.cluster}</td>
              <td className="rule-txt">{b.rule}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="small" style={{ marginTop: 10 }}>
        标 N/A 的书因依赖字段缺失而无法计算 —— 这不是「中性 50 分」。
      </div>
    </>
  )
}
