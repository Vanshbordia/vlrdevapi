import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getGuide, getGuides } from '@/lib/content'
import { MdxContent } from '@/components/mdx-content'
import { extractToc } from '@/components/toc'
import { TocLayout } from '@/components/toc-layout'
import { CtaSection } from '@/components/cta'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return getGuides().map((guide) => ({ slug: guide.slug }))
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  const { slug } = await props.params
  const guide = getGuide(slug)
  if (!guide) return {}

  return {
    title: guide.title,
    description: guide.description,
    openGraph: {
      title: `${guide.title} - VLRdevAPI Guides`,
      description: guide.description,
      type: 'article',
      publishedTime: guide.date,
    },
  }
}

export default async function GuidePage(props: Props) {
  const { slug } = await props.params
  const guide = getGuide(slug)
  if (!guide) notFound()

  const tocItems = extractToc(guide.content)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    headline: guide.title,
    description: guide.description,
    datePublished: guide.date,
    author: {
      '@type': 'Organization',
      name: guide.author,
      url: 'https://riftwatch.org',
    },
    publisher: {
      '@type': 'Organization',
      name: 'RiftWatch',
      url: 'https://riftwatch.org',
      logo: {
        '@type': 'ImageObject',
        url: 'https://vlrdevapi.pages.dev/logo.png',
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `https://vlrdevapi.pages.dev/guides/${guide.slug}`,
    },
    proficiencyLevel: 'Beginner',
    url: `https://vlrdevapi.pages.dev/guides/${guide.slug}`,
  }

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://vlrdevapi.pages.dev' },
      { '@type': 'ListItem', position: 2, name: 'Guides', item: 'https://vlrdevapi.pages.dev/guides' },
      { '@type': 'ListItem', position: 3, name: guide.title, item: `https://vlrdevapi.pages.dev/guides/${guide.slug}` },
    ],
  }

  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdBreadcrumb).replace(/</g, '\\u003c'),
        }}
      />
      <article>
        <div className="border-b border-border">
          <div className="mx-auto max-w-7xl px-6 pt-28 pb-12 md:pt-36 md:pb-16">
            <Link
              href="/guides"
              className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
              Back to Guides
            </Link>
            <time className="mt-6 block text-xs text-muted-foreground">{guide.date}</time>
            <h1 className="font-heading mt-2 text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl md:text-[2.75rem]">
              {guide.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
              {guide.description}
            </p>

          </div>
        </div>

        <div className="mx-auto max-w-7xl px-6 py-12 md:py-16">
          <TocLayout items={tocItems}>
            <MdxContent content={guide.content} />
            <CtaSection />
          </TocLayout>
        </div>
      </article>
    </main>
  )
}
