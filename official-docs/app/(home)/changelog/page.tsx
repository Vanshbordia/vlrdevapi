import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
}

const versions = [
  {
    version: '2.0.0',
    date: '7 July 2026',
    summary: 'Initial release of VLRdevAPI. A type-safe Python SDK for Valorant esports data from VLR.gg.',
    sections: [
      {
        title: 'Features',
        items: [
          'Match listings: live matches, upcoming with pagination (`matches.upcoming(page=2, return_all=True)`), completed with date filtering.',
          'Team data: info (name, tag, socials), roster with roles/captain/sub status, map stats with agent composition breakdowns, completed and upcoming matches, roster transactions, event placement history with prize winnings.',
          'Player profiles: basic info, current and past teams, agent usage stats (`30d`, `60d`, `90d`, `all`), match history with configurable limit, consolidated profile with top agents.',
          'Event/tournament coverage: list with tier/region/status filters, info (dates, prize pool, location), stages, teams, matches, standings.',
          'Series/match detail: full match overview (teams, scores, map veto, per-game breakdowns), VOD links (YouTube/Twitch), per-player performance stats with ratings, round-by-round data, economy analysis, kill matrices, advanced stats (aces, clutches, multi-kills).',
        ],
      },
      {
        title: 'API',
        items: [
          'Synchronous VLRClient with context manager support and curried access pattern (`client.team(4568).roster()`).',
          'Module-level convenience access via `import vlrdevapi` with a lazy-initialized default client.',
          'Pydantic v2 models with full type hints, field descriptions, and validation across all endpoints.',
          'Typed exception hierarchy: VLRdevError, NotFoundError, RequestError, RateLimitError, ParsingError, ValidationError.',
        ],
      },
      {
        title: 'Infrastructure',
        items: [
          'Automatic retry logic with configurable strategy (max retries, backoff factor, status codes).',
          'Rate limiting with configurable max requests per minute per namespace.',
          'LRU response caching with configurable TTL to reduce redundant requests.',
          'URL enrichment that automatically resolves team IDs and series info on match listings.',
          'Dependency management with uv for fast installs and reproducible builds.',
          'Supports Python 3.11 and later.',
        ],
      },
      {
        title: 'Documentation',
        items: [
          'Official documentation site at https://vlrdevapi.pages.dev built with Next.js 16 and Fumadocs.',
          'API reference covering every namespace, method, parameter, and return type.',
          'Practical examples for events, matches, teams, players, and cross-namespace queries.',
          'Getting started guide, quickstart tutorial, and development setup guide.',
          'Doc validation scripts (check_mdx_examples.py) that verify syntax and live execution of code examples in CI.',
          'GitHub Actions workflow for automatic doc validation on pull requests.',
          'Comprehensive test suite with fixture-based offline tests and live integration tests.',
        ],
      },
    ],
  },
]

const jsonLdBreadcrumb = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://vlrdevapi.pages.dev' },
    { '@type': 'ListItem', position: 2, name: 'Changelog', item: 'https://vlrdevapi.pages.dev/changelog/' },
  ],
}

const jsonLdWebPage = {
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  name: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
  url: 'https://vlrdevapi.pages.dev/changelog/',
  about: {
    '@type': 'SoftwareSourceCode',
    name: 'VLRdevAPI',
    programmingLanguage: 'Python',
    runtimePlatform: 'Python 3.11+',
    codeRepository: 'https://github.com/vanshbordia/vlrdevapi',
    author: [
      {
        '@type': 'Person',
        name: 'Vansh Bordia',
      },
      {
        '@type': 'Organization',
        name: 'RiftWatch',
        url: 'https://riftwatch.org',
      },
    ],
  },
}

export default function ChangelogPage() {
  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdBreadcrumb).replace(/</g, '\\u003c'),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdWebPage).replace(/</g, '\\u003c'),
        }}
      />
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 pt-28 pb-16 md:pt-36 md:pb-20">
          <h1 className="font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem]">
            Changelog
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            Track every release, feature, and fix in VLRdevAPI.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_1fr] lg:gap-16">
            {/* Sticky timeline sidebar */}
            <aside className="relative">
              <div className="lg:sticky lg:top-28 lg:self-start">
                <nav aria-label="Version timeline">
                  <ol className="relative border-l border-border">
                    {versions.map((v) => (
                      <li key={v.version} className="pl-6 pb-10 last:pb-0">
                        <div className="absolute left-0 top-1.5 -translate-x-1/2 size-3 rounded-full border-2 border-fd-primary bg-background" />
                        <time className="text-xs font-semibold uppercase tracking-widest text-fd-primary">
                          {v.date}
                        </time>
                        <p className="mt-1 text-sm font-bold text-foreground">
                          v{v.version}
                        </p>
                      </li>
                    ))}
                  </ol>
                </nav>
              </div>
            </aside>

            {/* Version entries */}
            <div className="min-w-0">
              {versions.map((v) => (
                <article key={v.version} id={v.version}>
                  <div className="mb-2 flex items-baseline gap-3 lg:hidden">
                    <time className="text-xs font-semibold uppercase tracking-widest text-fd-primary">
                      {v.date}
                    </time>
                    <span className="text-sm font-bold text-foreground">
                      v{v.version}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {v.summary}
                  </p>

                  {v.sections.map((section) => (
                    <div key={section.title} className="mt-8 first:mt-6">
                      <h3 className="text-sm font-bold text-foreground tracking-tight">
                        {section.title}
                      </h3>
                      <ul className="mt-3 space-y-2">
                        {section.items.map((item) => (
                          <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                            <span className="mt-[5px] size-1.5 shrink-0 rounded-full bg-border" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}

                  <div className="mt-8 flex items-center gap-4 border-t border-border pt-6">
                    <Link
                      href="https://github.com/vanshbordia/vlrdevapi/releases"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex h-9 items-center justify-center bg-foreground px-4 text-xs font-medium tracking-tight text-background transition-all hover:brightness-110"
                    >
                      View on GitHub
                    </Link>
                    <Link
                      href="https://pypi.org/project/vlrdevapi/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex h-9 items-center justify-center border border-border bg-background px-4 text-xs font-medium tracking-tight text-foreground transition-all hover:bg-muted"
                    >
                      Install from PyPI
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
