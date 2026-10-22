import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowUpRight } from 'lucide-react'
import { JsonLd } from '@/components/json-ld'
import { AnchorNav } from '@/components/marketing/anchor-nav'
import { FaqAccordion } from '@/components/marketing/faq-accordion'
import { canonicalUrl, siteUrl } from '@/lib/shared'
import { createPageMetadata } from '@/lib/seo'
import { project } from '@/lib/project'
import { ContentHero, IndexPanel } from '@/components/marketing/content-page'

export const metadata: Metadata = createPageMetadata({
  title: 'FAQ',
  description:
    'Frequently asked questions about VLRdevAPI, the type-safe Python SDK for Valorant esports data from VLR.gg.',
  path: '/faq/',
})

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
        a: <>VLRdevAPI is a Python SDK that provides a type-safe interface for fetching Valorant esports data from VLR.gg. It handles scraping, parsing, and data normalization so you can focus on building your application. See the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">documentation</Link> for full details.</>,
      },
      {
        q: 'Do I need an API key?',
        a: <>No. VLRdevAPI works without any API key or authentication. Just <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">uv add vlrdevapi</code> or <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install vlrdevapi</code> and start making calls.</>,
      },
      {
        q: 'What Python version is required?',
        a: <>Python 3.11 or later. The library uses modern Python features including type hints and Pydantic models.</>,
      },
      {
        q: 'How do I install VLRdevAPI?',
        a: <>Install with uv (recommended): <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">uv add vlrdevapi</code>. Or with pip: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install vlrdevapi</code>. See the <Link href="/docs/installation/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">installation guide</Link> for more options.</>,
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
        a: <>Yes. The built-in client respects a default rate limit to avoid overloading VLR.gg. You can configure the rate limit and retry behavior when creating a <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient</code> instance. See the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">API reference</Link> for configuration options.</>,
      },
      {
        q: 'Is VLRdevAPI synchronous or asynchronous?',
        a: <>Synchronous. Every method is a blocking call, so wrap independent fetches in a thread pool, or use <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">asyncio.to_thread</code> from an async framework such as FastAPI. Multi-stage endpoints already parallelize their stage pages internally.</>,
      },
      {
        q: 'What data can I access?',
        a: <>VLRdevAPI covers six namespaces: <strong className="font-medium text-white/85">matches</strong> (upcoming, live, completed), <strong className="font-medium text-white/85">team</strong> (info, roster, stats, placements), <strong className="font-medium text-white/85">player</strong> (profiles, agents, teams, match history), <strong className="font-medium text-white/85">event</strong> (stages, standings, teams, matches), <strong className="font-medium text-white/85">series</strong> (VODs, player stats, economy data, rounds), and <strong className="font-medium text-white/85">news</strong> (listings and full articles). Browse the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">full API reference</Link> for details.</>,
      },
      {
        q: 'Is VLRdevAPI production-ready?',
        a: <>It ships with error handling, retry logic, rate limiting, and typed exceptions for reliable operation. See the <Link href="/guides/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">getting started guide</Link> for best practices.</>,
      },
      {
        q: 'How do I handle errors?',
        a: <>VLRdevAPI provides a typed exception hierarchy: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">NotFoundError</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RateLimitError</code>, <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RequestError</code>, and more. Import from <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">vlrdevapi.exceptions</code> and handle them with standard try/except blocks.</>,
      },
      {
        q: 'How do I paginate through results?',
        a: <>List endpoints return paginated responses containing a list of entries and a <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">has_next_page</code> boolean. Pass <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">page=2</code> to request subsequent pages, or pass <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">return_all=True</code> to automatically fetch and combine all pages.</>,
      },
      {
        q: 'Can I filter data by date or region?',
        a: <>Some endpoints support optional parameters like date ranges and region filters. Check the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">API reference</Link> for each endpoint to see available query parameters.</>,
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
        a: <>VLRdevAPI abstracts away HTML parsing, rate limiting, and data normalization. It is faster, more reliable, and requires less code than scraping VLR.gg directly. Read the <Link href="/blog/vlrdevapi-vs-web-scraping/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">comparison post</Link> for a detailed breakdown.</>,
      },
      {
        q: 'Can I use VLRdevAPI in a Jupyter notebook?',
        a: <>Yes. Module-level access works directly in notebooks. Use <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">import vlrdevapi</code> and call methods synchronously.</>,
      },
      {
        q: 'How do I configure the client?',
        a: <>Pass options to the constructor: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient(timeout=30, max_retries=5, requests_per_second=2)</code>. Check the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">API reference</Link> for all options.</>,
      },
      {
        q: 'Does VLRdevAPI cache responses?',
        a: <>Within a single call, yes. Multi-stage endpoints reuse the pages they have already parsed instead of fetching them twice, so a request that spans several pages still makes one request per page.</>,
      },
      {
        q: 'What happens if VLR.gg is down?',
        a: <>The client raises a <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">RequestError</code> when it cannot reach VLR.gg. Configure retry logic to automatically retry on transient failures. Check the <Link href="/changelog/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">changelog</Link> for any known issues.</>,
      },
      {
        q: 'Can I contribute to the library itself?',
        a: <>Absolutely. The library is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">GitHub</Link>. Check the development setup guide in the docs to get started with local development.</>,
      },
    ],
  },
  {
    title: 'Troubleshooting',
    items: [
      {
        q: 'I get an import error when trying to use VLRdevAPI',
        a: <>Make sure you installed the package: <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip list | findstr vlrdevapi</code> (Windows) or <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip list | grep vlrdevapi</code> (macOS/Linux). If missing, run <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">uv add vlrdevapi</code> or <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">pip install --upgrade vlrdevapi</code>. Check that you are using Python 3.11+.</>,
      },
      {
        q: 'My API calls return no data',
        a: <>Check that the parameters you are passing are valid. For example, some endpoints require specific date formats or team IDs. If you are filtering by region or tier, verify that the filter values match the expected format. See the <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">API reference</Link> for exact parameter specifications.</>,
      },
      {
        q: 'VLRdevAPI is running slowly',
        a: <>Slow responses are usually due to rate limiting, network latency, or multi-page enrichment. You can configure <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">requests_per_second</code> and <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">timeout</code> on your <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient</code>. For endpoints supporting pagination, request only the records you need with <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">limit</code> instead of fetching all pages. See the <Link href="/guides/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">guides</Link> for performance tips.</>,
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
        a: <>VLR.gg frequently updates match statistics, rosters, and live scores. In-memory client instances cache team details during match enrichment for the lifetime of that client. If you suspect data has changed on VLR.gg, create a fresh <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">VLRClient</code> or wait a few minutes and try again. If a parser discrepancy persists, open an issue on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">GitHub</Link>.</>,
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
        a: <>For most projects, VLRdevAPI is faster to set up and more reliable than scraping. It handles markup changes, rate limiting, and data normalization automatically. Scraping gives you full control but requires ongoing maintenance. See the <Link href="/blog/vlrdevapi-vs-web-scraping/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">detailed comparison</Link> for a full breakdown.</>,
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
        a: <>VLRdevAPI is open source on <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">GitHub</Link>. Contributions are welcome: bug reports, feature requests, and pull requests are all appreciated. See the contributing guide in the repository.</>,
      },
      {
        q: 'What is the difference between the docs guides and the standalone guides?',
        a: <>The <Link href="/docs/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">docs section</Link> covers contributor guides (development setup, contributing) and the API reference. The standalone <Link href="/guides/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">guides</Link> section contains step-by-step tutorials for using the library. The <Link href="/blog/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">blog</Link> has news, updates, and comparisons.</>,
      },
      {
        q: 'Where can I report bugs or request features?',
        a: <>Open an issue on the <Link href="https://github.com/vanshbordia/vlrdevapi/issues" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">GitHub repository</Link>. Include the version you are using (check with <code className="border border-white/10 bg-white/[0.04] px-1.5 py-0.5 font-mono text-[12px] text-white/65">vlrdevapi.__version__</code>) and steps to reproduce.</>,
      },
      {
        q: 'What is the changelog and where can I find it?',
        a: <>The <Link href="/changelog/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">changelog</Link> tracks every release, feature, and fix in VLRdevAPI. It covers all versions with detailed section breakdowns.</>,
      },
      {
        q: 'Is there a community or Discord server?',
        a: <>Check the <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">GitHub repository</Link> for community links and discussions. Issues and pull requests are the primary way to engage with the project.</>,
      },
      {
        q: 'How often is VLRdevAPI updated?',
        a: <>Updates are published as needed when VLR.gg changes its markup or when new features are added. Follow the <Link href="/changelog/" className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary">changelog</Link> and GitHub releases for update notifications.</>,
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

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  name: `${project.name} FAQ`,
  description: 'Frequently asked questions about VLRdevAPI, the Python SDK for Valorant esports data.',
  url: canonicalUrl('/faq'),
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
  const totalQuestions = sections.reduce((total, section) => total + section.items.length, 0)

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />
      <ContentHero
        eyebrow="Support / FAQ"
        title={
          <>
            Frequently
            <br />
            <span className="text-fd-primary">asked.</span>
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
                  className="text-fd-primary underline underline-offset-2 decoration-fd-primary/30 transition-colors hover:decoration-fd-primary"
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
          className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
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
              <div className="lg:sticky lg:top-24 lg:self-start">
                <AnchorNav
                  label="Sections"
                  ariaLabel="FAQ sections"
                  items={sections.map((section, index) => ({
                    id: sectionId(section.title),
                    label: section.title,
                    meta: String(index + 1).padStart(2, '0'),
                  }))}
                />
              </div>
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
                      <span className="pb-0.5 font-mono text-[12px] text-fd-primary">
                        0{index + 1}
                      </span>
                      <h2 className="text-2xl font-medium tracking-[-0.03em] text-white">
                        {section.title}
                      </h2>
                    </div>
                    <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                      {section.items.length} questions
                    </span>
                  </div>
                  <div className="border-b border-white/10">
                    <FaqAccordion
                      items={section.items}
                      questionClassName="max-w-3xl text-left text-[15px] font-medium leading-relaxed text-white/80 transition-colors group-hover:text-white md:text-base"
                      answerClassName="max-w-3xl pb-5 pr-10 text-[14px] leading-relaxed text-white/55"
                    />
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
