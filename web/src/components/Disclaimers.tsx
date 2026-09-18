export default function Disclaimers({ items }: { items: string[] }) {
  if (!items?.length) return null
  return (
    <div className="card">
      <h2>这套分数的局限（必须随结论一起读）</h2>
      <ul className="disc">
        {items.map((d, i) => <li key={i}>{d}</li>)}
      </ul>
    </div>
  )
}
