'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

export type ChangelogSection = {
  title: string
  items: string[]
}

export type ChangelogVersion = {
  version: string
  date: string
  github: string
  pypi: string
  summary: string
  sections: ChangelogSection[]
}

export default function ChangelogTimeline({ versions }: { versions: ChangelogVersion[] }) {
  const [active, setActive] = useState(versions[0]?.version ?? '')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        let bestTop = -Infinity
        let best: string | null = null
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          if (entry.boundingClientRect.top > bestTop) {
            bestTop = entry.boundingClientRect.top
            best = entry.target.id
          }
        }
        if (best) setActive(best)
      },
      { rootMargin: '-80px 0px -80% 0px', threshold: 0 },
    )
    for (const v of versions) {
      const el = document.getElementById(v.version)
      if (el) observer.observe(el)
    }
    return () => observer.disconnect()
  }, [versions])

  return (
    <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_1fr] lg:gap-16">
      {/* Sticky timeline sidebar */}
      <aside className="relative">
        <div className="lg:sticky lg:top-28 lg:self-start">
          <nav aria-label="Version timeline">
            <ol className="relative border-l border-border">
              {versions.map((v) => {
                const isActive = active === v.version
                return (
                  <li key={v.version} className="pl-6 pb-10 last:pb-0">
                    <a
                      href={`#${v.version}`}
                      className="group block"
                      aria-current={isActive ? 'true' : undefined}
                    >
                      <time
                        className={`text-xs font-semibold uppercase tracking-widest transition-colors ${
                          isActive ? 'text-fd-primary' : 'text-fd-primary/60 group-hover:text-fd-primary'
                        }`}
                      >
                        {v.date}
                      </time>
                      <p
                        className={`mt-1 text-sm font-bold transition-colors ${
                          isActive ? 'text-foreground' : 'text-muted-foreground group-hover:text-foreground'
                        }`}
                      >
                        v{v.version}
                      </p>
                    </a>
                  </li>
                )
              })}
            </ol>
          </nav>
        </div>
      </aside>

      {/* Version entries */}
      <div className="min-w-0">
        {versions.map((v) => (
          <article key={v.version} id={v.version} className="scroll-mt-28 pb-16">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-3">
              <h2 className="text-xl font-bold tracking-tight text-foreground">
                v{v.version}
              </h2>
              <time className="text-xs font-semibold uppercase tracking-widest text-fd-primary">
                {v.date}
              </time>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {v.summary}
            </p>

            {v.sections.map((section) => (
              <div key={section.title} className="mt-8">
                <h3 className="text-sm font-bold tracking-tight text-foreground">
                  {section.title}
                </h3>
                <ul className="mt-3 space-y-2">
                  {section.items.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                      <span className="mt-[5px] size-1.5 shrink-0 rounded-full bg-border" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                href={v.github}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-9 items-center justify-center bg-foreground px-4 text-xs font-medium tracking-tight text-background transition-all hover:brightness-110"
              >
                View on GitHub
              </Link>
              <Link
                href={v.pypi}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-9 items-center justify-center border border-border bg-background px-4 text-xs font-medium tracking-tight text-foreground transition-all hover:bg-muted"
              >
                Install from PyPI
              </Link>
            </div>
            <div className="mt-8 border-t border-border" />
          </article>
        ))}
      </div>
    </div>
  )
}
