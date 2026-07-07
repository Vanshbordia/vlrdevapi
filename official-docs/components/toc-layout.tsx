'use client'

import type { ReactNode } from 'react'
import { TOCProvider, TOCScrollArea } from 'fumadocs-ui/components/toc'
import { TOCItems, TOCItem, TOCEmpty } from 'fumadocs-ui/components/toc/clerk'
import type { TocItem } from './toc'

interface TocLayoutProps {
  children: ReactNode
  items: TocItem[]
}

export function TocLayout({ children, items }: TocLayoutProps) {
  const tocItems = items.map((item) => ({
    title: item.text,
    url: `#${item.id}`,
    depth: item.level,
  }))

  return (
    <TOCProvider toc={tocItems}>
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-[1fr_200px]">
        <div className="min-w-0">
          {children}
        </div>
        <aside className="hidden lg:block">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <h2 className="text-xs font-semibold uppercase tracking-widest text-fd-muted-foreground mb-3">
              On this page
            </h2>
            <TOCScrollArea>
              <TOCItems>
                {tocItems.length === 0 ? (
                  <TOCEmpty />
                ) : (
                  tocItems.map((item) => <TOCItem key={item.url} item={item} />)
                )}
              </TOCItems>
            </TOCScrollArea>
          </div>
        </aside>
      </div>
    </TOCProvider>
  )
}
