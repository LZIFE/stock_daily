import type { Analysis } from '../types'

const BAND_TEXT: Record<string, string> = {
  BUY: '条件满足',
  WATCH: '观察',
  AVOID: '条件不满足',
  NO_DATA: '数据不足',
  EXCLUDED: '已排除',
}

export default function VerdictCard({ a }: { a: Analysis }) {
  const pctl = a.core_pctl ?? 0
  const br = a.badrate
  const imputed = a.core_imputed_books || []

  return (
    <div className="layer layer-fact">
      <h2>判定 · 事实层<span className="tag">已回测验证</span></h2>

      <div className="verdict">
        <div>
          <div className={`band ${a.band || ''}`}>{a.band || '—'}</div>
          <div className="small" style={{ marginTop: 6, textAlign: 'center' }}>
            {BAND_TEXT[a.band || ''] || ''}
          </div>
        </div>

        <div className="kv">
          <div>
            <div className="k">核心分</div>
            <div className="v">{a.core_score ?? '—'}</div>
          </div>
          <div>
            <div className="k">全市场分位</div>
            <div className="v">{a.core_pctl ?? '—'}</div>
            <div className="bar"><i style={{ width: `${pctl}%` }} /></div>
            <div className="small" style={{ marginTop: 4 }}>
              与 {a.n_tied ?? 0} 只并列，非精确排名
            </div>
          </div>
          <div>
            <div className="k">共识分（其余 28 本）</div>
            <div className="v">{a.consensus_score ?? '—'}</div>
          </div>
          <div>
            <div className="k">分歧（核心−共识）</div>
            <div className="v">
              {a.divergence != null ? (a.divergence > 0 ? '+' : '') + a.divergence : '—'}
            </div>
          </div>
          <div>
            <div className="k">该分桶历史坏率</div>
            <div className="v">{br ? `${br.bad_rate}%` : '—'}</div>
            <div className="small">基准 {br?.base_bad_rate ?? '—'}%（{br?.window}）</div>
          </div>
          <div>
            <div className="k">仓位上限</div>
            <div className="v">{a.position_cap_pct ?? '—'}%</div>
          </div>
        </div>
      </div>

      <div className="chips">
        <span className="chip">基准日 {a.asof}</span>
        <span className="chip">
          可用 {a.n_books_available ?? '—'}/{a.n_books_total ?? '—'} 本
        </span>
        {a.soft_demote.map(s => <span key={s} className="chip warn">降级：{s}</span>)}
        {a.flags.map(s => <span key={s} className="chip">标注：{s}</span>)}
        {!a.pe_available && <span className="chip warn">PE 不适用</span>}
        {a.loss_maker && <span className="chip bad">近12月亏损</span>}
        {a.quality_bad && <span className="chip warn">quality_bad</span>}
      </div>

      {imputed.length > 0 && (
        <div className="warnbox" style={{ marginTop: 12 }}>
          核心分中有 {imputed.length}/4 本书（{imputed.join('、')}）因数据缺失而使用兜底值参与计算。
          保留兜底是为了与回测口径一致（改掉就失去证据链），但该核心分并非完全由真实输入得出。
        </div>
      )}
    </div>
  )
}
