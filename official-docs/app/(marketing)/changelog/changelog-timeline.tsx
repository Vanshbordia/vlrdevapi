import Link from 'next/link'
import { ArrowUpRight } from 'lucide-react'
import { AnchorNav } from '@/components/marketing/anchor-nav'
import type { ChangelogVersion } from '@/lib/changelog'

export type { ChangelogSection, ChangelogVersion } from '@/lib/changelog'

/**
 * Anchor ids must be valid CSS identifiers, so `3.0.0` becomes `v3-0-0`.
 */
function versionAnchor(version: string) {
  return `v${version.replace(/\./g, '-')}`
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
  return (
    <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-16">
      <aside className="relative">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <AnchorNav
            label="Versions"
            ariaLabel="Version timeline"
            variant="stacked"
            note="Newest first"
            items={versions.map((version) => ({
              id: versionAnchor(version.version),
              label: `v${version.version}`,
              meta: version.date,
            }))}
          />
        </div>
      </aside>

      <div className="min-w-0">
        {versions.map((v, index) => (
          <article
            key={v.version}
            id={versionAnchor(v.version)}
            className="scroll-mt-24 border-b border-white/10 pb-14 last:border-b-0 last:pb-0 [&+article]:pt-14"
          >
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-[12px] text-fd-primary">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h2 className="text-2xl font-medium tracking-[-0.03em] text-white">
                v{v.version}
              </h2>
              {index === 0 ? (
                <span className="border border-fd-primary/40 bg-fd-primary/10 px-2 py-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-fd-primary">
                  Latest
                </span>
              ) : null}
              <time
                dateTime={v.isoDate}
                className="ml-auto font-mono text-[12px] uppercase tracking-[0.12em] text-fd-muted"
              >
                {v.date}
              </time>
            </div>

            <p className="mt-4 max-w-3xl text-[14px] leading-relaxed text-white/50">
              {v.summary}
            </p>

            <div className="mt-8 space-y-8">
              {v.sections.map((section) => (
                <div key={section.title}>
                  <h3 className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-primary">
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
                          className="mt-[10px] h-px w-3 shrink-0 bg-fd-primary/60"
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
                className="group inline-flex h-10 items-center gap-1.5 border border-white bg-white px-4 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
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
