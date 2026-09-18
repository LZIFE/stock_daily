import type { Analysis } from '../types'

export default function BooksPanel({ a }: { a: Analysis }) {
  const core = a.books.filter(b => b.core)
  const rest = a.books.filter(b => !b.core)

  return (
    <div className="layer layer-fact">
      <h2>29 本书的逐本观点 · 事实层<span className="tag">已回测验证</span></h2>

      <div className="zone">
        <strong>核心 4 本</strong> —— 在分类目标上被 walk-forward 验证过（纯样本外
        Q1 坏率 19.36% → Q5 4.52%，AUC 0.649）。<strong>只有这 4 本进入买入判定。</strong>
      </div>
      <table>
        <thead>
          <tr>
            <th style={{ width: 108 }}>书</th>
            <th style={{ width: 58 }}>分数</th>
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
              <td className="rule">{b.rule}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="zone">
        <strong>其余 25 本</strong> —— 29 本等权共识在 walk-forward 上 AUC 0.5237（≈随机）、
        spread 仅 2.39pp。<strong>这些分数不进入判定，仅展示「其他作者怎么看」。</strong>
      </div>
      <table>
        <thead>
          <tr>
            <th style={{ width: 108 }}>书</th>
            <th style={{ width: 58 }}>分数</th>
            <th style={{ width: 88 }}>簇</th>
            <th>规则</th>
          </tr>
        </thead>
        <tbody>
          {rest.map(b => (
            <tr key={b.name} className={b.available ? '' : 'unavail'}>
              <td>{b.name}</td>
              <td className="num">{b.available ? b.score : <span title="算不出来">N/A</span>}</td>
              <td className="small">{b.cluster}</td>
              <td className="rule">{b.rule}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="small" style={{ marginTop: 8 }}>
        标 N/A 的书因依赖字段缺失而无法计算 —— 这不是「中性 50 分」。
      </div>
    </div>
  )
}
