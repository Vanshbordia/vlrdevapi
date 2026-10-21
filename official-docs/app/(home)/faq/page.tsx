'use client'

import Link from 'next/link'
import { ArrowUpRight, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { canonicalUrl, siteUrl } from '@/lib/shared'
import { project } from '@/lib/project'
import { ContentHero, IndexPanel } from '@/components/marketing/content-page'
import { useActiveId } from '@/components/use-active-id'

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
        a: <>VLRdevAPI is a Python SDK that provides a type-safe interface for fetching Valorant esports data from VLR.gg. It handles scraping, parsing, and data normalization so you can focus on building your application. See the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">documentation</Link> for full details.</>,
      },
      {
        q: 'Do I need an API key?',
        a: <>No. VLRdevAPI works without any API key or authentication. Just <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install vlrdevapi</code> and start making calls.</>,
      },
      {
        q: 'What Python version is required?',
        a: <>Python 3.11 or later. The library uses modern Python features including type hints and Pydantic models.</>,
      },
      {
        q: 'How do I install VLRdevAPI?',
        a: <>Install with pip: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install vlrdevapi</code>. Or with uv (recommended): <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">uv add vlrdevapi</code>. See the <Link href="/docs/installation/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">installation guide</Link> for more options.</>,
      },
      {
        q: 'Can I try VLRdevAPI without installing it?',
        a: <>You can experiment with VLRdevAPI in your browser using a Python notebook on Google Colab or similar platforms. Just run <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install vlrdevapi</code> in a notebook cell and start exploring.</>,
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
        a: <>Yes. The built-in client respects a default rate limit to avoid overloading VLR.gg. You can configure the rate limit and retry behavior when creating a <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient</code> instance. See the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">API reference</Link> for configuration options.</>,
      },
      {
        q: 'Is VLRdevAPI synchronous or asynchronous?',
        a: <>Synchronous. Every method is a blocking call, so wrap independent fetches in a thread pool, or use <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">asyncio.to_thread</code> from an async framework such as FastAPI. Multi-stage endpoints already parallelize their stage pages internally.</>,
      },
      {
        q: 'What data can I access?',
        a: <>VLRdevAPI covers five namespaces: <strong className="font-medium text-white/85">matches</strong> (upcoming, live, completed), <strong className="font-medium text-white/85">teams</strong> (info, roster, stats, placements), <strong className="font-medium text-white/85">players</strong> (profiles, agents, teams, match history), <strong className="font-medium text-white/85">events</strong> (stages, standings, teams, matches), and <strong className="font-medium text-white/85">series</strong> (VODs, player stats, economy data, rounds). Browse the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">full API reference</Link> for details.</>,
      },
      {
        q: 'Is VLRdevAPI production-ready?',
        a: <>Yes. The library is used in production. It includes error handling, retry logic, rate limiting, and typed exceptions for reliable operation. See the <Link href="/guides/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">getting started guide</Link> for best practices.</>,
      },
      {
        q: 'How do I handle errors?',
        a: <>VLRdevAPI provides a typed exception hierarchy: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">NotFoundError</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RateLimitError</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RequestError</code>, and more. Import from <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">vlrdevapi.exceptions</code> and handle them with standard try/except blocks.</>,
      },
      {
        q: 'How do I paginate through results?',
        a: <>List endpoints return paginated responses with <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">.page</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">.total_pages</code>, and <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">.matches</code> properties. Use <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">page=2</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">return_all=True</code> to fetch all pages automatically.</>,
      },
      {
        q: 'Can I filter data by date or region?',
        a: <>Some endpoints support optional parameters like date ranges and region filters. Check the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">API reference</Link> for each endpoint to see available query parameters.</>,
      },
    ],
  },
  {
    title: 'Technical',
    items: [
      {
        q: 'Does VLRdevAPI have any dependencies?',
        a: <>The core dependency is Pydantic v2 for data modeling and validation. HTTP requests go through httpx.</>,
      },
      {
        q: 'How does VLRdevAPI compare to web scraping?',
        a: <>VLRdevAPI abstracts away HTML parsing, rate limiting, and data normalization. It is faster, more reliable, and requires less code than scraping VLR.gg directly. Read the <Link href="/blog/vlrdevapi-vs-web-scraping/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">comparison post</Link> for a detailed breakdown.</>,
      },
      {
        q: 'Can I use VLRdevAPI in a Jupyter notebook?',
        a: <>Yes. Module-level access works directly in notebooks. Use <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">import vlrdevapi</code> and call methods synchronously.</>,
      },
      {
        q: 'How do I configure the client?',
        a: <>Pass options to <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient(timeout=30, max_retries=5, rate_limit_per_minute=20)</code> or set environment variables. Check the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">API reference</Link> for all options.</>,
      },
      {
        q: 'Does VLRdevAPI cache responses?',
        a: <>Yes. The client includes an LRU response cache with configurable TTL to reduce redundant requests. Disable or adjust caching by passing <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">cache_ttl=0</code> to <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient</code>.</>,
      },
      {
        q: 'What happens if VLR.gg is down?',
        a: <>The client raises a <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RequestError</code> when it cannot reach VLR.gg. Configure retry logic to automatically retry on transient failures. Check the <Link href="/changelog/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">changelog</Link> for any known issues.</>,
      },
      {
        q: 'Can I contribute to the library itself?',
        a: <>Absolutely. The library is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">GitHub</Link>. Check the development setup guide in the docs to get started with local development.</>,
      },
    ],
  },
  {
    title: 'Troubleshooting',
    items: [
      {
        q: 'I get an import error when trying to use VLRdevAPI',
        a: <>Make sure you installed the package: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip list | findstr vlrdevapi</code> (Windows) or <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip list | grep vlrdevapi</code> (macOS/Linux). If missing, run <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install --upgrade vlrdevapi</code>. Check that you are using Python 3.11+.</>,
      },
      {
        q: 'My API calls return no data',
        a: <>Check that the parameters you are passing are valid. For example, some endpoints require specific date formats or team IDs. If you are filtering by region or tier, verify that the filter values match the expected format. See the <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">API reference</Link> for exact parameter specifications.</>,
      },
      {
        q: 'VLRdevAPI is running slowly',
        a: <>Slow responses are usually due to rate limiting or network latency. Increase the rate limit on your VLRClient if you have permission, or reduce the frequency of your requests. The library includes retry logic and caching -- enable caching to avoid redundant calls. See the <Link href="/guides/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">guides</Link> for performance tips.</>,
      },
      {
        q: 'I get a RateLimitError. What should I do?',
        a: <>Reduce the frequency of your requests or raise the <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">requests_per_second</code> setting on your VLRClient. The default limit is conservative to protect both your application and VLR.gg. Spacing requests out over longer intervals usually helps more than fetching in parallel.</>,
      },
      {
        q: 'How do I enable debug logging?',
        a: <>Set the log level to DEBUG in your application. VLRdevAPI uses Python&apos;s standard logging module. Add <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">import logging; logging.basicConfig(level=logging.DEBUG)</code> to see detailed information about requests, responses, and caching behavior.</>,
      },
      {
        q: 'The data I get does not match what I see on VLR.gg',
        a: <>Data is fetched and cached at different times. There may be a brief delay between when data appears on VLR.gg and when it is available through the API. Clear your client cache or wait a few minutes and try again. If the discrepancy persists, open an issue on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">GitHub</Link>.</>,
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
        a: <>For most projects, VLRdevAPI is faster to set up and more reliable than scraping. It handles markup changes, rate limiting, and data normalization automatically. Scraping gives you full control but requires ongoing maintenance. See the <Link href="/blog/vlrdevapi-vs-web-scraping/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">detailed comparison</Link> for a full breakdown.</>,
      },
      {
        q: 'Is VLRdevAPI better than BeautifulSoup for this use case?',
        a: <>Yes, for Valorant esports data. BeautifulSoup requires you to write and maintain CSS selectors for every data point, handle pagination manually, and build your own rate limiting and caching. VLRdevAPI gives you all of that out of the box with a clean Pythonic interface. Use BeautifulSoup if you need data from sources not covered by VLRdevAPI.</>,
      },
      {
        q: 'Can I use VLRdevAPI with frameworks like FastAPI or Django?',
        a: <>Yes. VLRdevAPI works with any Python web framework. It is synchronous, so call it directly from Django or Flask views, and in FastAPI or another async framework run calls in a thread with <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">asyncio.to_thread</code> so the event loop stays free.</>,
      },
    ],
  },
  {
    title: 'Project',
    items: [
      {
        q: 'Is this project affiliated with Riot Games or VLR.gg?',
        a: <>No. VLRdevAPI is an independent open-source project. It is not affiliated with, endorsed by, or connected to Riot Games or VLR.gg.</>,
      },
      {
        q: 'How can I contribute?',
        a: <>VLRdevAPI is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">GitHub</Link>. Contributions are welcome: bug reports, feature requests, and pull requests are all appreciated. See the contributing guide in the repository.</>,
      },
      {
        q: 'What is the difference between the docs guides and the standalone guides?',
        a: <>The <Link href="/docs/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">docs section</Link> covers contributor guides (development setup, contributing) and the API reference. The standalone <Link href="/guides/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">guides</Link> section contains step-by-step tutorials for using the library. The <Link href="/blog/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">blog</Link> has news, updates, and comparisons.</>,
      },
      {
        q: 'Where can I report bugs or request features?',
        a: <>Open an issue on the <Link href="https://github.com/vanshbordia/vlrdevapi/issues" target="_blank" rel="noopener noreferrer" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">GitHub repository</Link>. Include the version you are using (check with <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">vlrdevapi.__version__</code>) and steps to reproduce.</>,
      },
      {
        q: 'What is the changelog and where can I find it?',
        a: <>The <Link href="/changelog/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">changelog</Link> tracks every release, feature, and fix in VLRdevAPI. It covers all versions with detailed section breakdowns.</>,
      },
      {
        q: 'Is there a community or Discord server?',
        a: <>Check the <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">GitHub repository</Link> for community links and discussions. Issues and pull requests are the primary way to engage with the project.</>,
      },
      {
        q: 'How often is VLRdevAPI updated?',
        a: <>Updates are published as needed when VLR.gg changes its markup or when new features are added. Follow the <Link href="/changelog/" className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]">changelog</Link> and GitHub releases for update notifications.</>,
      },
      {
        q: 'Can I use VLRdevAPI in a commercial project?',
        a: <>Yes. VLRdevAPI is open source under the MIT license. You can use it in personal, academic, and commercial projects. See the LICENSE file on GitHub for full terms.</>,
      },
    ],
  },
]

function sectionId(title: string) {
  return `section-${title.toLowerCase().replace(/\s+/g, '-')}`
}

const sectionIds = sections.map((section) => sectionId(section.title))

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  name: `${project.name} FAQ`,
  description: 'Frequently asked questions about VLRdevAPI, the Python SDK for Valorant esports data.',
  url: canonicalUrl('/faq/'),
  inLanguage: 'en',
  publisher: { '@id': `${siteUrl}/#organization` },
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
  const activeSection = useActiveId(sectionIds)
  const totalQuestions = sections.reduce((total, section) => total + section.items.length, 0)

  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />
      <ContentHero
        eyebrow="Support / FAQ"
        title={
          <>
            Frequently
            <br />
            <span className="text-[#ff4655]">asked.</span>
          </>
        }
        description="Everything you need to know about the VLRdevAPI Python SDK, from installation and rate limits to typed errors, pagination, and production use."
        aside={
          <IndexPanel
            label="FAQ index"
            rows={[
              { label: 'Questions', value: String(totalQuestions).padStart(2, '0') },
              { label: 'Sections', value: String(sections.length).padStart(2, '0') },
              { label: 'Python', value: '3.11+' },
              { label: 'API key', value: 'Not required' },
            ]}
            note={
              <>
                Still stuck?{' '}
                <Link
                  href="https://github.com/vanshbordia/vlrdevapi/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#ff8d97] underline underline-offset-2 decoration-[#ff4655]/30 transition-colors hover:decoration-[#ff4655]"
                >
                  Open an issue
                </Link>
                .
              </>
            }
          />
        }
      >
        <Link
          href="/docs/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
        >
          Read the docs
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
        <Link
          href="/guides/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white/15 px-5 text-[13px] font-medium text-white/65 transition-colors hover:border-white/30 hover:text-white"
        >
          Browse guides
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      </ContentHero>

      <section>
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-16">
            <aside className="relative">
              <nav aria-label="FAQ sections" className="lg:sticky lg:top-24 lg:self-start">
                <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
                  Sections
                </p>
                <ol className="mt-4 border-l border-white/10">
                  {sections.map((section, index) => {
                    const id = sectionId(section.title)
                    const isActive = activeSection === id

                    return (
                      <li key={section.title}>
                        <a
                          href={`#${id}`}
                          aria-current={isActive ? 'location' : undefined}
                          className={`-ml-px flex items-center gap-3 border-l py-2.5 pl-4 text-[13px] transition-colors ${
                            isActive
                              ? 'border-[#ff4655] text-white'
                              : 'border-transparent text-white/40 hover:text-white/75'
                          }`}
                        >
                          <span className="font-mono text-[12px] text-white/25">
                            0{index + 1}
                          </span>
                          {section.title}
                        </a>
                      </li>
                    )
                  })}
                </ol>
              </nav>
            </aside>

            <div className="min-w-0 space-y-14">
              {sections.map((section, index) => (
                <article
                  key={section.title}
                  id={sectionId(section.title)}
                  className="scroll-mt-24"
                >
                  <div className="flex flex-wrap items-end justify-between gap-3 border-b border-white/10 pb-4">
                    <div className="flex items-end gap-3">
                      <span className="pb-0.5 font-mono text-[12px] text-[#ff4655]">
                        0{index + 1}
                      </span>
                      <h2 className="text-2xl font-medium tracking-[-0.03em] text-white">
                        {section.title}
                      </h2>
                    </div>
                    <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                      {section.items.length} questions
                    </span>
                  </div>
                  <dl className="border-b border-white/10">
                    {section.items.map((item) => (
                      <FaqBlock key={item.q} item={item} />
                    ))}
                  </dl>
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
    <div className="group border-b border-white/10 last:border-b-0">
      <dt className="text-[15px] font-medium leading-relaxed text-white/75 transition-colors group-hover:text-white md:text-base">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          className="flex w-full items-start justify-between gap-6 py-5 text-left"
        >
          <span className="max-w-3xl">{item.q}</span>
          <span
            aria-hidden="true"
            className={`mt-0.5 flex size-7 shrink-0 items-center justify-center border transition-colors ${
              open
                ? 'border-[#ff4655]/40 bg-[#ff4655]/10 text-[#ff8d97]'
                : 'border-white/10 text-white/30 group-hover:border-white/25 group-hover:text-white/60'
            }`}
          >
            <ChevronDown
              className={`size-3.5 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
            />
          </span>
        </button>
      </dt>
      <dd
        className={`grid transition-all duration-200 ${
          open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="max-w-3xl pb-5 pr-10 text-[14px] leading-relaxed text-white/45">
            {item.a}
          </div>
        </div>
      </dd>
    </div>
  )
}
