import { useState } from 'react'
import type { Interpretation } from '../types'

/** 把 "[规则:邱国鹭] 正文" / "[事件:标题] 正文" 渲染成带引用标记的样式。 */
function Cite({ text }: { text: string }) {
  const m = /^(\[(?:规则|事件):[^\]]*\])\s*([\s\S]*)$/.exec(text || '')
  if (!m) return <>{text}</>
  return (
    <>
      <span className="cite">{m[1]}</span>
      {m[2]}
    </>
  )
}

export default function AIPanel({
  data, loading, error, onFirstOpen,
}: {
  data: Interpretation | null
  loading: boolean
  error: string | null
  /** 首次展开时才触发生成 —— 不展开就不花这次调用 */
  onFirstOpen?: () => void
}) {
  // 默认折叠：AI 层未经验证，不应抢在判定之前影响判断
  const [open, setOpen] = useState(false)
  const [fired, setFired] = useState(false)

  const toggle = () => {
    setOpen(o => !o)
    if (!fired) { setFired(true); onFirstOpen?.() }
  }

  return (
    <div className="layer layer-ai">
      <div className="ai-fold" onClick={toggle}>
        <h2 style={{ margin: 0 }}>
          AI 解读 <span className="tag">未经回测验证</span>
        </h2>
        <span className="chev">{open ? '收起 ▲' : '展开 ▼'}</span>
      </div>

      {!open && (
        <div className="small" style={{ marginTop: 8 }}>
          本层由模型生成，只做解释与补充，<strong>不得改变判定</strong>。默认折叠。
        </div>
      )}

      {open && (
        <div style={{ marginTop: 12 }}>
          {loading && <div className="skel">正在生成解读（实测 12–60s）…</div>}
          {error && <div className="err">AI 解读不可用：{error}。以下判定与分数不受影响。</div>}

          {data?.degraded && (
            <div className="warnbox">
              已降级为纯规则报告：{(data.warnings || []).join('；') || '模型不可用'}
            </div>
          )}

          {data?.sections && (
            <>
              <p className="headline">{data.sections.headline}</p>

              {!!data.sections.core_book_explanation?.length && (
                <div className="sec">
                  <b>核心 4 本在说什么</b>
                  <ul>
                    {data.sections.core_book_explanation.map((x, i) => (
                      <li key={i}>
                        <strong>{x.book}</strong>（{x.score}）：<Cite text={x.reading} />
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {data.sections.consensus_panel?.summary && (
                <div className="sec">
                  <b>29 本的整体分布</b>
                  <div style={{ fontSize: 13 }}>{data.sections.consensus_panel.summary}</div>
                  {data.sections.consensus_panel.divergence_reading && (
                    <div className="small" style={{ marginTop: 4 }}>
                      分歧：{data.sections.consensus_panel.divergence_reading}
                    </div>
                  )}
                </div>
              )}

              {!!data.sections.event_scan?.length && (
                <div className="sec">
                  <b>公告 / 研报扫描</b>
                  <ul>
                    {data.sections.event_scan.map((e, i) => (
                      <li key={i}>
                        <span className="small">{e.date}</span>{' '}
                        {e.title}
                        {e.unverified && <span className="unv">未经独立核实</span>}
                        <div className="small"><Cite text={e.why} /></div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!!data.sections.risks_rules_cannot_see?.length && (
                <div className="sec">
                  <b>规则看不到的风险</b>
                  <ul>
                    {data.sections.risks_rules_cannot_see.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}

              {!!data.sections.what_would_change_the_verdict?.length && (
                <div className="sec">
                  <b>什么会改变这个判定</b>
                  <ul>
                    {data.sections.what_would_change_the_verdict.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}

              {!!data.sections.data_limits?.length && (
                <div className="sec">
                  <b>数据限制</b>
                  <ul>
                    {data.sections.data_limits.map((r, i) => <li key={i} className="small">{r}</li>)}
                  </ul>
                </div>
              )}

              <div className="small" style={{ marginTop: 12 }}>
                模型 {data.model} · 提示词 {data.prompt_version} · {data.generated_at}
                {data.cached && ' · 缓存'}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
