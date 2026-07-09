import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { blogSource } from '@/lib/source'
import { getMDXComponents } from '@/components/mdx'
import { TocLayout } from '@/components/toc-layout'
import { extractToc } from '@/components/toc'
import { CtaSection } from '@/components/cta'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return blogSource.getPages().map((page) => ({ slug: page.slugs[0] }))
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  const { slug } = await props.params
  const page = blogSource.getPage([slug])
  if (!page) return {}

  return {
    title: page.data.title,
    description: page.data.description,
    openGraph: {
      title: `${page.data.title} - VLRdevAPI Blog`,
      description: page.data.description,
      url: `https://vlrdevapi.pages.dev/blog/${slug}/`,
      type: 'article',
      publishedTime: page.data.date,
    },
  }
}

export default async function BlogPostPage(props: Props) {
  const { slug } = await props.params
  const page = blogSource.getPage([slug])
  if (!page) notFound()

  const rawContent = await page.data.getText('processed')
  const tocItems = extractToc(rawContent ?? '')

  const MDX = page.data.body

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: page.data.title,
    description: page.data.description,
    datePublished: page.data.date,
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
      '@id': `https://vlrdevapi.pages.dev/blog/${slug}/`,
    },
    url: `https://vlrdevapi.pages.dev/blog/${slug}/`,
  }

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://vlrdevapi.pages.dev' },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: 'https://vlrdevapi.pages.dev/blog/' },
      { '@type': 'ListItem', position: 3, name: page.data.title, item: `https://vlrdevapi.pages.dev/blog/${slug}/` },
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
              href="/blog/"
              className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
              Back to Blog
            </Link>
            <time className="mt-6 block text-xs text-muted-foreground">{page.data.date}</time>
            <h1 className="font-heading mt-2 text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl md:text-[2.75rem]">
              {page.data.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
              {page.data.description}
            </p>

          </div>
        </div>

        <div className="mx-auto max-w-7xl px-6 py-12 md:py-16">
          <TocLayout items={tocItems}>
            <div className="prose prose-sm prose-neutral dark:prose-invert max-w-none prose-code:before:content-none prose-code:after:content-none prose-pre:!p-0 prose-pre:!bg-transparent prose-pre:!border-none prose-a:!font-normal prose-a:!no-underline [&_pre]:!bg-transparent [&_pre]:!p-0">
              <MDX components={getMDXComponents()} />
            </div>
            <CtaSection />
          </TocLayout>
        </div>
      </article>
    </main>
  )
}
