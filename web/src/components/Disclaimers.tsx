export default function Disclaimers({ items }: { items: string[] }) {
  if (!items?.length) return null
  return (
    <ul className="disc">
      {items.map((d, i) => <li key={i}>{d}</li>)}
    </ul>
  )
}
