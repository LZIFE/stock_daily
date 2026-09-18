import type { Analysis } from '../types'

const BAND_TEXT: Record<string, string> = {
  BUY: '条件满足',
  WATCH: '观察',
  AVOID: '条件不满足',
  NO_DATA: '数据不足',
  EXCLUDED: '已排除',
}

export default function Verdict({ a }: { a: Analysis }) {
  const pctl = a.core_pctl ?? 0
  const br = a.badrate
  const imputed = a.core_imputed_books || []
  const chg = a.change_pct
  const up = chg != null && chg > 0

  return (
    <>
      {/* 身份 + 判定：同行基线对齐，不做「大数字+小标签」的模板 */}
      <div className="verdict-row">
        <span className="who">
          {a.name || '—'}
          <span className="cd">{a.code}</span>
        </span>
        {a.price != null && (
          <span className="px">
            {a.price}
            {chg != null && (
              <span className={`chg ${up ? 'up' : 'down'}`}>
                {up ? '+' : ''}{chg}%
              </span>
            )}
          </span>
        )}
        <span style={{ flex: 1 }} />
        <span className="stamp">
          <span className={`bd ${a.band || ''}`}>{a.band || '—'}</span>
          <span className="txt">{BAND_TEXT[a.band || ''] || ''}</span>
        </span>
      </div>

      {/* 核心分：与说明同行，像正文里的强调 */}
      <div className="scoreline">
        <span className="n">{a.core_score ?? '—'}</span>
        <span className="unit">
          核心分 · 4 本等权
          <br />
          全市场 {a.core_pctl ?? '—'} 分位
        </span>
        <span className="gap" />
        <span className="unit" style={{ textAlign: 'right' }}>
          与 {a.n_tied ?? 0} 只并列
          <br />
          分位是区间，不是名次
        </span>
      </div>

      {/* 分位刻度：细线 + 阈值刻度，不用填充条 */}
      <div className="scale">
        <div className="rail">
          <span className="fill" style={{ width: `${Math.min(Math.max(pctl, 0), 100)}%` }} />
          <span className="tick" style={{ left: '0%' }} />
          <span className="tick thr" style={{ left: '90%' }} title="BUY 阈值：90 分位" />
          <span className="tick" style={{ left: '100%' }} />
          <span className="knob" style={{ left: `${Math.min(Math.max(pctl, 0), 100)}%` }} />
        </div>
        <div className="lbl">
          <span>0</span>
          <span className="thrlbl">↑ 90 分位 = BUY 阈值</span>
          <span>100</span>
        </div>
      </div>

      {/* 指标：定义列表，不是卡片网格 */}
      <dl className="facts">
        <div className="row">
          <dt>
            共识分（其余 28 本）
            <small>仅观点展示，不参与判定</small>
          </dt>
          <dd>{a.consensus_score ?? '—'}</dd>
        </div>
        <div className="row">
          <dt>
            分歧（核心 − 共识）
            <small>正值 = 核心 4 本比其余 28 本更看好</small>
          </dt>
          <dd style={{ color: (a.divergence ?? 0) >= 0 ? 'var(--buy)' : 'var(--vermil)' }}>
            {a.divergence != null ? (a.divergence > 0 ? '+' : '') + a.divergence : '—'}
          </dd>
        </div>
        <div className="row">
          <dt>
            该分桶历史坏率
            <small>未来 60 日跌超 20% 的比例 · 基准 {br?.base_bad_rate ?? '—'}%</small>
          </dt>
          <dd>{br ? `${br.bad_rate}%` : '—'}</dd>
        </div>
        <div className="row">
          <dt>
            仓位上限
            <small>流动性标注只压仓位，不改判定</small>
          </dt>
          <dd>{a.position_cap_pct ?? '—'}%</dd>
        </div>
        <div className="row">
          <dt>
            可算书数
            <small>N/A 是「算不出来」，不是中性 50</small>
          </dt>
          <dd>
            {a.n_books_available ?? '—'}/{a.n_books_total ?? '—'}
          </dd>
        </div>
      </dl>

      {(a.soft_demote.length > 0 || a.flags.length > 0 || !a.pe_available
        || a.loss_maker || a.quality_bad) && (
        <div className="small" style={{ marginTop: 14 }}>
          {a.soft_demote.length > 0 && <>降级：{a.soft_demote.join('、')}　</>}
          {a.flags.length > 0 && <>标注：{a.flags.join('、')}　</>}
          {!a.pe_available && <>PE 不适用　</>}
          {a.loss_maker && <>近 12 月亏损　</>}
          {a.quality_bad && <>quality_bad</>}
        </div>
      )}

      {imputed.length > 0 && (
        <div className="warnbox">
          核心分中有 {imputed.length}/4 本书（{imputed.join('、')}）因数据缺失而使用兜底值参与计算。
          保留兜底是为了与回测口径一致（改掉就失去证据链），但该核心分并非完全由真实输入得出。
        </div>
      )}
    </>
  )
}
