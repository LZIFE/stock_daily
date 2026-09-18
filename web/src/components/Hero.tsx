import type { Analysis } from '../types'

const BAND_TEXT: Record<string, string> = {
  BUY: '条件满足',
  WATCH: '观察',
  AVOID: '条件不满足',
  NO_DATA: '数据不足',
  EXCLUDED: '已排除',
}

export default function Hero({ a }: { a: Analysis }) {
  const pctl = a.core_pctl ?? 0
  const br = a.badrate
  const imputed = a.core_imputed_books || []
  const chg = a.change_pct
  const up = chg != null && chg > 0

  return (
    <div className="layer layer-fact">
      <h2>判定 · 事实层<span className="tag">已回测验证</span></h2>

      <div className="hero">
        {/* 股票身份 */}
        <div className="hero-id">
          <div className="nm">{a.name || '—'}</div>
          <div className="cd">{a.code}</div>
          {a.price != null && (
            <div className="px">
              {a.price}
              {chg != null && (
                <span className={`chg ${up ? 'up' : 'down'}`}>
                  {up ? '+' : ''}{chg}%
                </span>
              )}
            </div>
          )}
        </div>

        {/* 判定 */}
        <div className="band-box">
          <div className={`band ${a.band || ''}`}>{a.band || '—'}</div>
          <div className="band-note">{BAND_TEXT[a.band || ''] || ''}</div>
        </div>

        {/* 大分数 + 分位轨道 */}
        <div className="score-hero">
          <div className="n">{a.core_score ?? '—'}</div>
          <div className="lb">核心分（4 本等权）</div>
          <div className="track">
            <div className="bar">
              <i style={{ width: `${Math.min(Math.max(pctl, 0), 100)}%` }} />
              <span className="mk" style={{ left: '90%' }} title="BUY 阈值 90 分位" />
            </div>
            <div className="sc"><span>0</span><span>90 分位</span><span>100</span></div>
          </div>
          <div className="rk">
            全市场 {a.core_pctl ?? '—'} 分位 · 与 {a.n_tied ?? 0} 只并列
          </div>
        </div>
      </div>

      {/* 指标网格 */}
      <div className="kv" style={{ marginTop: 20 }}>
        <div>
          <div className="k">共识分（其余 28 本）</div>
          <div className="v">{a.consensus_score ?? '—'}</div>
          <div className="h">仅观点展示，不参与判定</div>
        </div>
        <div>
          <div className="k">分歧（核心 − 共识）</div>
          <div className="v">
            {a.divergence != null ? (a.divergence > 0 ? '+' : '') + a.divergence : '—'}
          </div>
          <div className="h">正值＝核心 4 本比其余更看好</div>
        </div>
        <div>
          <div className="k">该分桶历史坏率</div>
          <div className="v">{br ? `${br.bad_rate}%` : '—'}</div>
          <div className="h">基准 {br?.base_bad_rate ?? '—'}%（{br?.window}）</div>
        </div>
        <div>
          <div className="k">仓位上限</div>
          <div className="v">{a.position_cap_pct ?? '—'}%</div>
          <div className="h">流动性标注只压仓位</div>
        </div>
        <div>
          <div className="k">可算书数</div>
          <div className="v">{a.n_books_available ?? '—'}/{a.n_books_total ?? '—'}</div>
          <div className="h">N/A 不是中性 50</div>
        </div>
      </div>

      {/* 状态标签 */}
      <div className="chips">
        <span className="chip">基准日 {a.asof}</span>
        {a.soft_demote.map(s => <span key={s} className="chip warn">降级 · {s}</span>)}
        {a.flags.map(s => <span key={s} className="chip">标注 · {s}</span>)}
        {!a.pe_available && <span className="chip warn">PE 不适用</span>}
        {a.loss_maker && <span className="chip bad">近 12 月亏损</span>}
        {a.quality_bad && <span className="chip warn">quality_bad</span>}
        {imputed.length === 0 && <span className="chip ok">核心分输入完整</span>}
      </div>

      {imputed.length > 0 && (
        <div className="warnbox">
          核心分中有 {imputed.length}/4 本书（{imputed.join('、')}）因数据缺失而使用兜底值参与计算。
          保留兜底是为了与回测口径一致（改掉就失去证据链），但该核心分并非完全由真实输入得出。
        </div>
      )}
    </div>
  )
}
