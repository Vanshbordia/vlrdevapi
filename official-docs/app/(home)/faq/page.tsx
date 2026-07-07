'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

interface FaqItem {
  q: string
  a: React.ReactNode
}

interface FaqSection {
  title: string
  items: FaqItem[]
}

const sections: FaqSection[] = [
  {
    title: 'Getting Started',
    items: [
      {
        q: 'What is VLRdevAPI?',
        a: <>VLRdevAPI is a Python SDK that provides a type-safe interface for fetching Valorant esports data from VLR.gg. It handles scraping, parsing, and data normalization so you can focus on building your application. See the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">documentation</Link> for full details.</>,
      },
      {
        q: 'Do I need an API key?',
        a: <>No. VLRdevAPI works without any API key or authentication. Just <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip install vlrdevapi</code> and start making calls.</>,
      },
      {
        q: 'What Python version is required?',
        a: <>Python 3.11 or later. The library uses modern Python features including type hints and async support.</>,
      },
      {
        q: 'How do I install VLRdevAPI?',
        a: <>Install with pip: <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip install vlrdevapi</code>. Or with uv (recommended): <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">uv add vlrdevapi</code>. See the <Link href="/docs/installation" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">installation guide</Link> for more options.</>,
      },
      {
        q: 'Can I try VLRdevAPI without installing it?',
        a: <>You can experiment with VLRdevAPI in your browser using a Python notebook on Google Colab or similar platforms. Just run <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip install vlrdevapi</code> in a notebook cell and start exploring.</>,
      },
      {
        q: 'Does VLRdevAPI work on Windows, macOS, and Linux?',
        a: <>Yes. VLRdevAPI is pure Python and works on all major operating systems. It has been tested on Windows 10/11, macOS, and Ubuntu Linux.</>,
      },
    ],
  },
  {
    title: 'Usage',
    items: [
      {
        q: 'Does VLRdevAPI have rate limits?',
        a: <>Yes. The built-in client respects a default rate limit to avoid overloading VLR.gg. You can configure the rate limit and retry behavior when creating a <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">VLRClient</code> instance. See the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">API reference</Link> for configuration options.</>,
      },
      {
        q: 'Can I use VLRdevAPI asynchronously?',
        a: <>Yes. Both module-level access (sync) and async client are supported. Use <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">VLRClient</code> with <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">async with</code> for concurrent data fetching. Check the <Link href="/guides" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">guides</Link> for async examples.</>,
      },
      {
        q: 'What data can I access?',
        a: <>VLRdevAPI covers five namespaces: <strong className="text-foreground font-medium">matches</strong> (upcoming, live, completed), <strong className="text-foreground font-medium">teams</strong> (info, roster, stats, placements), <strong className="text-foreground font-medium">players</strong> (profiles, agents, teams, match history), <strong className="text-foreground font-medium">events</strong> (stages, standings, teams, matches), and <strong className="text-foreground font-medium">series</strong> (VODs, player stats, economy data, rounds). Browse the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">full API reference</Link> for details.</>,
      },
      {
        q: 'Is VLRdevAPI production-ready?',
        a: <>Yes. The library is used in production by RiftWatch and the community. It includes error handling, retry logic, rate limiting, and typed exceptions for reliable operation. See the <Link href="/guides" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">getting started guide</Link> for best practices.</>,
      },
      {
        q: 'How do I handle errors?',
        a: <>VLRdevAPI provides a typed exception hierarchy: <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">NotFoundError</code>, <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">RateLimitError</code>, <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">RequestError</code>, and more. Import from <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">vlrdevapi.exceptions</code> and handle them with standard try/except blocks.</>,
      },
      {
        q: 'How do I paginate through results?',
        a: <>List endpoints return paginated responses with <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">.page</code>, <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">.total_pages</code>, and <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">.matches</code> properties. Use <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">page=2</code>, <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">return_all=True</code> to fetch all pages automatically.</>,
      },
      {
        q: 'Can I filter data by date or region?',
        a: <>Some endpoints support optional parameters like date ranges and region filters. Check the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">API reference</Link> for each endpoint to see available query parameters.</>,
      },
    ],
  },
  {
    title: 'Technical',
    items: [
      {
        q: 'Does VLRdevAPI have any dependencies?',
        a: <>The core dependency is Pydantic v2 for data modeling and validation. The async client uses httpx for HTTP requests.</>,
      },
      {
        q: 'How does VLRdevAPI compare to web scraping?',
        a: <>VLRdevAPI abstracts away HTML parsing, rate limiting, and data normalization. It is faster, more reliable, and requires less code than scraping VLR.gg directly. Read the <Link href="/blog/vlrdevapi-vs-web-scraping" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">comparison post</Link> for a detailed breakdown.</>,
      },
      {
        q: 'Can I use VLRdevAPI in a Jupyter notebook?',
        a: <>Yes. Module-level access works directly in notebooks. Use <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">import vlrdevapi</code> and call methods synchronously.</>,
      },
      {
        q: 'How do I configure the client?',
        a: <>Pass options to <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">VLRClient(timeout=30, max_retries=5, rate_limit_per_minute=20)</code> or set environment variables. Check the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">API reference</Link> for all options.</>,
      },
      {
        q: 'Does VLRdevAPI cache responses?',
        a: <>Yes. The client includes an LRU response cache with configurable TTL to reduce redundant requests. Disable or adjust caching by passing <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">cache_ttl=0</code> to <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">VLRClient</code>.</>,
      },
      {
        q: 'What happens if VLR.gg is down?',
        a: <>The client raises a <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">RequestError</code> when it cannot reach VLR.gg. Configure retry logic to automatically retry on transient failures. Check the <Link href="/changelog" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">changelog</Link> for any known issues.</>,
      },
      {
        q: 'Can I contribute to the library itself?',
        a: <>Absolutely. The library is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">GitHub</Link>. Check the development setup guide in the docs to get started with local development.</>,
      },
    ],
  },
  {
    title: 'Troubleshooting',
    items: [
      {
        q: 'I get an import error when trying to use VLRdevAPI',
        a: <>Make sure you installed the package: <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip list | findstr vlrdevapi</code> (Windows) or <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip list | grep vlrdevapi</code> (macOS/Linux). If missing, run <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">pip install --upgrade vlrdevapi</code>. Check that you are using Python 3.11+.</>,
      },
      {
        q: 'My API calls return no data',
        a: <>Check that the parameters you are passing are valid. For example, some endpoints require specific date formats or team IDs. If you are filtering by region or tier, verify that the filter values match the expected format. See the <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">API reference</Link> for exact parameter specifications.</>,
      },
      {
        q: 'VLRdevAPI is running slowly',
        a: <>Slow responses are usually due to rate limiting or network latency. Increase the rate limit on your VLRClient if you have permission, or reduce the frequency of your requests. The library includes retry logic and caching -- enable caching to avoid redundant calls. See the <Link href="/guides" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">guides</Link> for performance tips.</>,
      },
      {
        q: 'I get a RateLimitError. What should I do?',
        a: <>Reduce the frequency of your requests or increase the <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">rate_limit_per_minute</code> setting on your VLRClient. The default limit is conservative to protect both your application and VLR.gg. Consider spreading requests across longer intervals or using the async client for concurrent fetching with built-in throttling.</>,
      },
      {
        q: 'How do I enable debug logging?',
        a: <>Set the log level to DEBUG in your application. VLRdevAPI uses Python's standard logging module. Add <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">import logging; logging.basicConfig(level=logging.DEBUG)</code> to see detailed information about requests, responses, and caching behavior.</>,
      },
      {
        q: 'The data I get does not match what I see on VLR.gg',
        a: <>Data is fetched and cached at different times. There may be a brief delay between when data appears on VLR.gg and when it is available through the API. Clear your client cache or wait a few minutes and try again. If the discrepancy persists, open an issue on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">GitHub</Link>.</>,
      },
    ],
  },
  {
    title: 'Comparison',
    items: [
      {
        q: 'How does VLRdevAPI compare to other Valorant esports APIs?',
        a: <>VLRdevAPI is the only dedicated Python SDK for VLR.gg data. Unlike general-purpose scraping tools, it provides typed models, automatic normalization, built-in rate limiting, and a clean namespace structure. Other options include scraping VLR.gg directly or using third-party APIs that may require API keys or have usage limits.</>,
      },
      {
        q: 'Should I use VLRdevAPI or scrape VLR.gg directly?',
        a: <>For most projects, VLRdevAPI is faster to set up and more reliable than scraping. It handles markup changes, rate limiting, and data normalization automatically. Scraping gives you full control but requires ongoing maintenance. See the <Link href="/blog/vlrdevapi-vs-web-scraping" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">detailed comparison</Link> for a full breakdown.</>,
      },
      {
        q: 'Is VLRdevAPI better than BeautifulSoup for this use case?',
        a: <>Yes, for Valorant esports data. BeautifulSoup requires you to write and maintain CSS selectors for every data point, handle pagination manually, and build your own rate limiting and caching. VLRdevAPI gives you all of that out of the box with a clean Pythonic interface. Use BeautifulSoup if you need data from sources not covered by VLRdevAPI.</>,
      },
      {
        q: 'Can I use VLRdevAPI with frameworks like FastAPI or Django?',
        a: <>Yes. VLRdevAPI works with any Python web framework. Use the async client with FastAPI for non-blocking request handling, or the sync client with Django views. Both patterns are supported and documented in the <Link href="/guides" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">guides</Link>.</>,
      },
    ],
  },
  {
    title: 'Project',
    items: [
      {
        q: 'Is this project affiliated with Riot Games or VLR.gg?',
        a: <>No. VLRdevAPI is an independent open-source project by <Link href="https://riftwatch.org" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">RiftWatch</Link>. It is not affiliated with, endorsed by, or connected to Riot Games or VLR.gg.</>,
      },
      {
        q: 'How can I contribute?',
        a: <>VLRdevAPI is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">GitHub</Link>. Contributions are welcome: bug reports, feature requests, and pull requests are all appreciated. See the contributing guide in the repository.</>,
      },
      {
        q: 'What is the difference between the docs guides and the standalone guides?',
        a: <>The <Link href="/docs" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">docs section</Link> covers contributor guides (development setup, contributing) and the API reference. The standalone <Link href="/guides" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">guides</Link> section contains step-by-step tutorials for using the library. The <Link href="/blog" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">blog</Link> has news, updates, and comparisons.</>,
      },
      {
        q: 'Where can I report bugs or request features?',
        a: <>Open an issue on the <Link href="https://github.com/vanshbordia/vlrdevapi/issues" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">GitHub repository</Link>. Include the version you are using (check with <code className="text-sm font-normal text-foreground bg-muted px-1 py-0.5">vlrdevapi.__version__</code>) and steps to reproduce.</>,
      },
      {
        q: 'What is the changelog and where can I find it?',
        a: <>The <Link href="/changelog" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">changelog</Link> tracks every release, feature, and fix in VLRdevAPI. It covers all versions with detailed section breakdowns.</>,
      },
      {
        q: 'Is there a community or Discord server?',
        a: <>Check the <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">GitHub repository</Link> for community links and discussions. Issues and pull requests are the primary way to engage with the project.</>,
      },
      {
        q: 'How often is VLRdevAPI updated?',
        a: <>Updates are published as needed when VLR.gg changes its markup or when new features are added. Follow the <Link href="/changelog" className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary">changelog</Link> and GitHub releases for update notifications.</>,
      },
      {
        q: 'Can I use VLRdevAPI in a commercial project?',
        a: <>Yes. VLRdevAPI is open source under the MIT license. You can use it in personal, academic, and commercial projects. See the LICENSE file on GitHub for full terms.</>,
      },
    ],
  },
]

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  name: 'VLRdevAPI FAQ',
  description: 'Frequently asked questions about VLRdevAPI, the Python SDK for Valorant esports data.',
  url: 'https://vlrdevapi.pages.dev/faq',
  mainEntity: sections.flatMap((section) =>
    section.items.map((item) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: extractText(item.a),
      },
    }))
  ),
}

function extractText(node: React.ReactNode): string {
  if (typeof node === 'string') return node
  if (typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(extractText).join('')
  if (node && typeof node === 'object' && 'props' in node) {
    const children = (node as { props: { children: React.ReactNode } }).props.children
    return extractText(children)
  }
  return ''
}

export default function FaqPage() {
  const [activeSection, setActiveSection] = useState<string>('')

  const sectionIds = sections.map(
    (s) => `section-${s.title.toLowerCase().replace(/\s+/g, '-')}`
  )

  useEffect(() => {
    if (sectionIds.length === 0) return

    const ratios = new Map<string, number>()

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          ratios.set(entry.target.id, entry.intersectionRatio)
        }
        let bestId = ''
        let bestRatio = 0
        for (const id of sectionIds) {
          const r = ratios.get(id) || 0
          if (r > bestRatio) {
            bestRatio = r
            bestId = id
          }
        }
        if (bestId) setActiveSection(bestId)
      },
      {
        rootMargin: '-80px 0px 0px 0px',
        threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
      }
    )

    for (const id of sectionIds) {
      const el = document.getElementById(id)
      if (el) observer.observe(el)
    }

    return () => observer.disconnect()
  }, [sectionIds])

  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 pt-28 pb-16 md:pt-36 md:pb-20">
          <h1 className="font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem]">
            FAQ
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            Frequently asked questions about VLRdevAPI.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_1fr] lg:gap-16">
            {/* Sticky section nav */}
            <aside className="relative">
              <nav className="lg:sticky lg:top-28 lg:self-start">
                <div>
                  <ol className="relative border-l border-border">
                    {sections.map((section) => {
                      const id = `section-${section.title.toLowerCase().replace(/\s+/g, '-')}`
                      const isActive = activeSection === id
                      return (
                        <li key={section.title} className="pl-6 pb-8 last:pb-0">
                          <a
                            href={`#${id}`}
                            className={`text-xs font-semibold uppercase tracking-widest transition-colors ${
                              isActive
                                ? 'text-fd-primary'
                                : 'text-muted-foreground hover:text-fd-primary'
                            }`}
                          >
                            {section.title}
                          </a>
                        </li>
                      )
                    })}
                  </ol>
                </div>
              </nav>
            </aside>

            {/* FAQ sections */}
            <div className="min-w-0">
              {sections.map((section) => (
                <article
                  key={section.title}
                  id={`section-${section.title.toLowerCase().replace(/\s+/g, '-')}`}
                  className="scroll-mt-28"
                >
                  <h2 className="font-heading text-xl font-bold text-foreground tracking-tight lg:text-2xl">
                    {section.title}
                  </h2>
                  <dl className="mt-4 divide-y divide-border">
                    {section.items.map((item) => (
                      <FaqBlock key={item.q} item={item} />
                    ))}
                  </dl>
                  {sections.indexOf(section) < sections.length - 1 && (
                    <div className="my-12 border-t border-border" />
                  )}
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

function FaqBlock({ item }: { item: FaqItem }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="py-4 first:pt-0 last:pb-0">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-3 text-left"
      >
        <dt className="text-base font-semibold text-foreground md:text-[1.0625rem]">
          {item.q}
        </dt>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`shrink-0 text-muted-foreground transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      <div
        className={`overflow-hidden transition-all duration-200 ${open ? 'mt-2 max-h-96' : 'max-h-0'}`}
      >
        <dd className="text-sm leading-relaxed text-muted-foreground">
          {item.a}
        </dd>
      </div>
    </div>
  )
}
