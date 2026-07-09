import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getBlogPost, getBlogPosts } from '@/lib/content'
import { MdxContent } from '@/components/mdx-content'
import { extractToc } from '@/components/toc'
import { TocLayout } from '@/components/toc-layout'
import { CtaSection } from '@/components/cta'

interface Props {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return getBlogPosts().map((post) => ({ slug: post.slug }))
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  const { slug } = await props.params
  const post = getBlogPost(slug)
  if (!post) return {}

  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: `${post.title} - VLRdevAPI Blog`,
      description: post.description,
      url: `https://vlrdevapi.pages.dev/blog/${post.slug}/`,
      type: 'article',
      publishedTime: post.date,
    },
  }
}

export default async function BlogPostPage(props: Props) {
  const { slug } = await props.params
  const post = getBlogPost(slug)
  if (!post) notFound()

  const tocItems = extractToc(post.content)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.description,
    datePublished: post.date,
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
      '@id': `https://vlrdevapi.pages.dev/blog/${post.slug}/`,
    },
    url: `https://vlrdevapi.pages.dev/blog/${post.slug}/`,
  }

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://vlrdevapi.pages.dev' },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: 'https://vlrdevapi.pages.dev/blog/' },
      { '@type': 'ListItem', position: 3, name: post.title, item: `https://vlrdevapi.pages.dev/blog/${post.slug}/` },
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
            <time className="mt-6 block text-xs text-muted-foreground">{post.date}</time>
            <h1 className="font-heading mt-2 text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl md:text-[2.75rem]">
              {post.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
              {post.description}
            </p>

          </div>
        </div>

        <div className="mx-auto max-w-7xl px-6 py-12 md:py-16">
          <TocLayout items={tocItems}>
            <MdxContent content={post.content} />
            <CtaSection />
          </TocLayout>
        </div>
      </article>
    </main>
  )
}
