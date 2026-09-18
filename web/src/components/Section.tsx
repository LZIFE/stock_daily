import type { ReactNode } from 'react'

/**
 * 章节骨架：左侧边注栏（编号 + 来源标记）+ 竖直规线 + 正文。
 *
 * 这个结构承担两件事：
 *  1. 研究笔记的视觉语言 —— 编号、边注、规线，而不是一叠卡片
 *  2. **诚实性表达** —— 每一节在边注栏里标明它是「证据」还是「批注」，
 *     读者不必读完正文就知道该给多少信任
 */
export default function Section({
  n, title, tag, tagSub, lede, layer = 'fact', children,
}: {
  n: string
  title: string
  /** 边注栏第一行，如「已回测验证」/「未经回测验证」 */
  tag?: string
  /** 边注栏第二行，小字补充 */
  tagSub?: ReactNode
  /** 标题下的一句话说明 */
  lede?: ReactNode
  layer?: 'fact' | 'ai'
  children: ReactNode
}) {
  return (
    <section className={`sec${layer === 'ai' ? ' sec--ai' : ''}`}>
      <div className="sec-margin">
        <span className="sec-n">§{n}</span>
        {tag && (
          <span className="sec-tag">
            <b>{tag}</b>
            {tagSub}
          </span>
        )}
      </div>
      <div className="sec-body">
        <h2>{title}</h2>
        {lede && <p className="sec-lede">{lede}</p>}
        {children}
      </div>
    </section>
  )
}
