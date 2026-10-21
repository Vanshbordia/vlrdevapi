'use client'

import Link from 'next/link'
import { ArrowUpRight } from 'lucide-react'
import { useActiveId } from '@/components/use-active-id'

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

function renderInline(value: string) {
  return value.split(/(`[^`]+`)/g).map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code
          key={index}
          className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65 [overflow-wrap:anywhere]"
        >
          {part.slice(1, -1)}
        </code>
      )
    }

    return <span key={index}>{part}</span>
  })
}

export default function ChangelogTimeline({ versions }: { versions: ChangelogVersion[] }) {
  const active = useActiveId(versions.map((version) => version.version))

  return (
    <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-16">
      <aside className="relative">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
            Versions
          </p>
          <nav aria-label="Version timeline" className="mt-4">
            <ol className="border-l border-white/10">
              {versions.map((v) => {
                const isActive = active === v.version
                return (
                  <li key={v.version}>
                    <a
                      href={`#${v.version}`}
                      className={`group -ml-px flex flex-col gap-1 border-l py-2.5 pl-4 transition-colors ${
                        isActive
                          ? 'border-[#ff4655] text-white'
                          : 'border-transparent text-white/40 hover:text-white/75'
                      }`}
                      aria-current={isActive ? 'location' : undefined}
                    >
                      <span className="font-mono text-[12px] uppercase tracking-[0.12em] text-[#ff8d97]">
                        {v.date}
                      </span>
                      <span className="text-[13px] font-medium">v{v.version}</span>
                    </a>
                  </li>
                )
              })}
            </ol>
          </nav>
          <p className="mt-6 border-t border-white/10 pt-4 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
            Newest first
          </p>
        </div>
      </aside>

      <div className="min-w-0">
        {versions.map((v, index) => (
          <article
            key={v.version}
            id={v.version}
            className="scroll-mt-24 border-b border-white/10 pb-14 last:border-b-0 last:pb-0 [&+article]:pt-14"
          >
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-[12px] text-[#ff4655]">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h2 className="text-2xl font-medium tracking-[-0.03em] text-white">
                v{v.version}
              </h2>
              {index === 0 ? (
                <span className="border border-[#ff4655]/40 bg-[#ff4655]/10 px-2 py-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-[#ff8d97]">
                  Latest
                </span>
              ) : null}
              <time className="ml-auto font-mono text-[12px] uppercase tracking-[0.12em] text-white/25">
                {v.date}
              </time>
            </div>

            <p className="mt-4 max-w-3xl text-[14px] leading-relaxed text-white/50">
              {v.summary}
            </p>

            <div className="mt-8 space-y-8">
              {v.sections.map((section) => (
                <div key={section.title}>
                  <h3 className="font-mono text-[12px] uppercase tracking-[0.16em] text-[#ff8d97]">
                    {section.title}
                  </h3>
                  <ul className="mt-3 space-y-3">
                    {section.items.map((item, itemIndex) => (
                      <li
                        key={itemIndex}
                        className="flex items-start gap-3 text-[13.5px] leading-relaxed text-white/50"
                      >
                        <span
                          aria-hidden="true"
                          className="mt-[10px] h-px w-3 shrink-0 bg-[#ff4655]/60"
                        />
                        <span className="min-w-0">{renderInline(item)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href={v.github}
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex h-10 items-center gap-1.5 border border-white bg-white px-4 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
              >
                View on GitHub
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <Link
                href={v.pypi}
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex h-10 items-center gap-1.5 border border-white/15 px-4 text-[13px] font-medium text-white/60 transition-colors hover:border-white/30 hover:text-white"
              >
                Install from PyPI
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
