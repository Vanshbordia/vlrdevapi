import type { Metadata, ResolvingMetadata } from 'next'
import { notFound } from 'next/navigation'
import { guidesSource, getGuideEntries } from '@/lib/source'
import { getMDXComponents } from '@/components/mdx'
import { JsonLd } from '@/components/json-ld'
import { TocLayout } from '@/components/toc-layout'
import { toTocItems } from '@/components/toc'
import { CtaSection } from '@/components/cta'
import { ArticleHero, RelatedLinks } from '@/components/marketing/content-page'
import { ArticleBody } from '@/components/marketing/article-body'
import { canonicalUrl, siteUrl } from '@/lib/shared'
import { createPageMetadata, getOgImage, resolveOgImage, toIsoDateTime } from '@/lib/seo'
import { project, projectAuthor, projectUrls } from '@/lib/project'

export async function generateStaticParams() {
  return guidesSource.getPages().map((page) => ({ slug: page.slugs[0] }))
}

export async function generateMetadata(props: PageProps<'/guides/[slug]'>, parent: ResolvingMetadata): Promise<Metadata> {
  const { slug } = await props.params
  // The Open Graph image comes from the `opengraph-image` file convention in
  // this segment. Next has already generated its URL, so it is picked up from
  // the resolved metadata and reused for the JSON-LD.
  await resolveOgImage(`/guides/${slug}`, parent)

  const page = guidesSource.getPage([slug])
  if (!page) return {}

  const description = page.data.description ?? `Read ${page.data.title} on VLRdevAPI.`

  return createPageMetadata({
    title: page.data.title,
    description,
    path: `/guides/${slug}/`,
    type: 'article',
    openGraph: {
      publishedTime: toIsoDateTime(page.data.date),
      modifiedTime: page.data.lastModified?.toISOString(),
      authors: [page.data.author],
    },
  })
}

export default async function GuidePage(props: PageProps<'/guides/[slug]'>) {
  const { slug } = await props.params
  const page = guidesSource.getPage([slug])
  if (!page) notFound()

  const tocItems = toTocItems(page.data.toc)

  const MDX = page.data.body

  const canonical = canonicalUrl(`/guides/${slug}`)
  const ogImage = await getOgImage(`/guides/${slug}`)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    '@id': `${canonical}#article`,
    mainEntityOfPage: { '@type': 'WebPage', '@id': canonical },
    headline: page.data.title,
    description: page.data.description,
    // `image` is recommended for Google to grant article rich results. It is
    // the Open Graph image the `opengraph-image` file convention generated
    // for this route.
    ...(ogImage ? { image: [ogImage] } : {}),
    datePublished: toIsoDateTime(page.data.date),
    dateModified: page.data.lastModified?.toISOString() ?? toIsoDateTime(page.data.date),
    inLanguage: 'en',
    author: projectAuthor,
    publisher: { '@id': `${siteUrl}/#organization` },
    isPartOf: {
      '@id': `${canonicalUrl('/guides')}#collection`,
      name: `${project.name} Guides`,
    },
    url: canonical,
  }

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: projectUrls.home },
      { '@type': 'ListItem', position: 2, name: 'Guides', item: canonicalUrl('/guides') },
      { '@type': 'ListItem', position: 3, name: page.data.title, item: canonical },
    ],
  }

  // Other guides, newest first. Keeps the guide pages from being dead ends.
  const relatedLinks = getGuideEntries()
    .filter((guide) => guide.slug !== slug)
    .slice(0, 3)
    .map((guide) => ({ href: `${guide.url}/`, label: guide.title }))

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />
      <JsonLd data={jsonLdBreadcrumb} />
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
            <ArticleBody>
              <MDX components={getMDXComponents()} />
            </ArticleBody>
            <CtaSection />
          </TocLayout>
        </div>

        <RelatedLinks title="Related reading" links={relatedLinks} />
      </article>
    </main>
  )
}
