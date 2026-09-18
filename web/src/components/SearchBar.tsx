import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { SearchItem } from '../types'

export default function SearchBar({ onPick }: { onPick: (code: string) => void }) {
  const [q, setQ] = useState('')
  const [items, setItems] = useState<SearchItem[]>([])
  const [open, setOpen] = useState(false)
  const box = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!q.trim()) { setItems([]); return }
    const t = setTimeout(() => {
      api.search(q.trim()).then(r => { setItems(r.items); setOpen(true) }).catch(() => {})
    }, 220)
    return () => clearTimeout(t)
  }, [q])

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const bandOf = (b: string | null) => b || ''

  return (
    <div className="search" ref={box}>
      <input
        value={q}
        placeholder="输入股票代码或名称，例如 600519 / 茅台"
        onChange={e => setQ(e.target.value)}
        onFocus={() => items.length && setOpen(true)}
        onKeyDown={e => {
          if (e.key === 'Enter' && items[0]) { onPick(items[0].code); setOpen(false) }
        }}
      />
      {open && items.length > 0 && (
        <div className="sugg">
          {items.map(i => (
            <div key={i.code} onClick={() => { onPick(i.code); setOpen(false); setQ('') }}>
              <span className="c">{i.code}</span>
              <span>{i.name}</span>
              <span style={{ marginLeft: 'auto' }} className={`chip ${bandOf(i.band) === 'AVOID' ? '' : 'warn'}`}>
                {i.band} · {i.core_score ?? '—'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
