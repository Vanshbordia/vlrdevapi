import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { guidesSource } from '@/lib/source'
import { getMDXComponents } from '@/components/mdx'
import { TocLayout } from '@/components/toc-layout'
import { extractToc } from '@/components/toc'
import { CtaSection } from '@/components/cta'
import { ArticleHero } from '@/components/marketing/content-page'
import { canonicalUrl, siteUrl } from '@/lib/shared'
import { project, projectAuthor, projectUrls } from '@/lib/project'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return guidesSource.getPages().map((page) => ({ slug: page.slugs[0] }))
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  const { slug } = await props.params
  const page = guidesSource.getPage([slug])
  if (!page) return {}

  return {
    title: page.data.title,
    description: page.data.description,
    alternates: { canonical: canonicalUrl(`/guides/${slug}`) },
    openGraph: {
      title: `${page.data.title} - VLRdevAPI Guides`,
      description: page.data.description,
      url: canonicalUrl(`/guides/${slug}`),
      type: 'article',
      publishedTime: page.data.date,
    },
  }
}

export default async function GuidePage(props: Props) {
  const { slug } = await props.params
  const page = guidesSource.getPage([slug])
  if (!page) notFound()

  const rawContent = await page.data.getText('processed')
  const tocItems = extractToc(rawContent ?? '')

  const MDX = page.data.body

  const canonical = canonicalUrl(`/guides/${slug}`)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    headline: page.data.title,
    description: page.data.description,
    datePublished: page.data.date,
    inLanguage: 'en',
    author: projectAuthor,
    publisher: { '@id': `${siteUrl}/#organization` },
    isPartOf: {
      '@type': 'CollectionPage',
      '@id': canonicalUrl('/guides/'),
      name: `${project.name} Guides`,
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': canonical,
    },
    url: canonical,
  }

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: projectUrls.home },
      { '@type': 'ListItem', position: 2, name: 'Guides', item: canonicalUrl('/guides/') },
      { '@type': 'ListItem', position: 3, name: page.data.title, item: canonical },
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
        <ArticleHero
          backHref="/guides/"
          backLabel="All guides"
          kind="Guide"
          date={page.data.date}
          title={page.data.title}
          description={page.data.description}
        />

        <div className="mx-auto w-full max-w-5xl px-5 py-12 sm:px-8 md:py-16">
          <TocLayout items={tocItems}>
            <div className="article-prose prose prose-invert max-w-none prose-headings:scroll-mt-24 prose-headings:font-medium prose-headings:tracking-tight prose-h2:mt-12 prose-h2:text-2xl prose-h2:text-white prose-h3:text-lg prose-h3:text-white/90 prose-p:text-white/55 prose-p:leading-relaxed prose-li:text-white/55 prose-li:leading-relaxed prose-strong:text-white/85 prose-a:text-[#ff8d97] prose-a:font-normal [&_h2_a]:!text-inherit [&_h3_a]:!text-inherit [&_h4_a]:!text-inherit prose-a:no-underline hover:prose-a:underline prose-code:text-[#ffb3ba] prose-code:before:content-none prose-code:after:content-none prose-pre:!border prose-pre:!border-white/10 prose-pre:!bg-[#070707] prose-pre:!p-0 prose-blockquote:border-[#ff4655]/50 prose-blockquote:text-white/45 prose-hr:border-white/10 prose-table:text-white/55 prose-th:text-white/70 prose-td:border-white/10 [&_pre]:!bg-[#070707] [&_figure.shiki]:!my-6 [&_figure.shiki]:!rounded-none [&_figure.shiki]:!border-white/10 [&_figure.shiki]:!bg-[#070707] [&_figure.shiki]:!shadow-none">
              <MDX components={getMDXComponents()} />
            </div>
            <CtaSection />
          </TocLayout>
        </div>
      </article>
    </main>
  )
}
