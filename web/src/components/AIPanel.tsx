import { useEffect, useState } from 'react'
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
  // 默认折叠：批注未经回测验证，不该抢在证据之前影响判断。
  // 支持 ?ai=1 深链接直接展开（分享给他人时可以直接指向批注）。
  const wantOpen = new URLSearchParams(location.search).get('ai') === '1'
  const [open, setOpen] = useState(wantOpen)
  const [fired, setFired] = useState(wantOpen)

  useEffect(() => {
    if (wantOpen) onFirstOpen?.()
    // 仅在挂载时按 URL 决定是否自动拉取，之后交给用户点击
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const toggle = () => {
    setOpen(o => !o)
    if (!fired) { setFired(true); onFirstOpen?.() }
  }

  return (
    <>
      <div
        className="fold"
        role="button"
        tabIndex={0}
        aria-expanded={open}
        onClick={toggle}
        onKeyDown={e => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle() }
        }}
      >
        <span className="small">
          {open
            ? '收起这段批注'
            : '这段解读由模型生成，只做解释与补充，不得改变判定。点开才生成（不点不调用）。'}
        </span>
        <span className="chev">{open ? '收起 ▲' : '展开 ▼'}</span>
      </div>

      {open && (
        <div style={{ marginTop: 16 }}>
          {loading && <div className="skel">正在生成批注（实测 12–60s）…</div>}
          {error && <div className="err">批注不可用：{error}。判定与分数不受影响。</div>}

          {data?.degraded && (
            <div className="warnbox">
              已降级为纯规则报告：{(data.warnings || []).join('；') || '模型不可用'}
            </div>
          )}

          {data?.sections && (
            <>
              <p className="headline">{data.sections.headline}</p>

              {!!data.sections.core_book_explanation?.length && (
                <div className="anno">
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
                <div className="anno">
                  <b>29 本的整体分布</b>
                  <div style={{ fontSize: 13.5 }}>{data.sections.consensus_panel.summary}</div>
                  {data.sections.consensus_panel.divergence_reading && (
                    <div className="small" style={{ marginTop: 5 }}>
                      分歧：{data.sections.consensus_panel.divergence_reading}
                    </div>
                  )}
                </div>
              )}

              {!!data.sections.event_scan?.length && (
                <div className="anno">
                  <b>公告 / 研报扫描</b>
                  <ul>
                    {data.sections.event_scan.map((e, i) => (
                      <li key={i}>
                        <span className="small">{e.date}</span> {e.title}
                        {e.unverified && <span className="unv">未经独立核实</span>}
                        <div className="small"><Cite text={e.why} /></div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!!data.sections.risks_rules_cannot_see?.length && (
                <div className="anno">
                  <b>规则看不到的风险</b>
                  <ul>
                    {data.sections.risks_rules_cannot_see.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}

              {!!data.sections.what_would_change_the_verdict?.length && (
                <div className="anno">
                  <b>什么会改变这个判定</b>
                  <ul>
                    {data.sections.what_would_change_the_verdict.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}

              {!!data.sections.data_limits?.length && (
                <div className="anno">
                  <b>数据限制</b>
                  <ul>
                    {data.sections.data_limits.map((r, i) => <li key={i} className="small">{r}</li>)}
                  </ul>
                </div>
              )}

              <div className="small" style={{ marginTop: 18 }}>
                模型 {data.model} · 提示词 {data.prompt_version} · {data.generated_at}
                {data.cached && ' · 缓存'}
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}
