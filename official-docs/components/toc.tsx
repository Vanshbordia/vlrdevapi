export interface TocItem {
  id: string
  text: string
  level: number
}

export function extractToc(markdown: string): TocItem[] {
  const headingRegex = /^(#{2,3})\s+(.+?)(?:\s*[\[{]#([\w-]+)[\]}])?$/gm
  const items: TocItem[] = []
  let match: RegExpExecArray | null

  while ((match = headingRegex.exec(markdown)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const id = match[3] ?? text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')

    items.push({ id, text, level })
  }

  return items
}

export function TableOfContents({ items }: { items: TocItem[] }) {
  if (items.length === 0) return null

  return (
    <nav className="lg:sticky lg:top-28 lg:self-start">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
        On this page
      </h2>
      <ul className="space-y-2.5">
        {items.map((item) => (
          <li key={item.id}>
            <a
              href={`#${item.id}`}
              className={`block text-xs leading-snug text-muted-foreground hover:text-foreground transition-colors ${
                item.level === 3 ? 'pl-3' : ''
              }`}
            >
              {item.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}
