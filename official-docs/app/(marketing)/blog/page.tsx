import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { getBlogEntries } from '@/lib/source';
import { JsonLd } from '@/components/json-ld';
import { canonicalUrl, siteUrl } from '@/lib/shared';
import { createPageMetadata, toIsoDateTime } from '@/lib/seo';
import { project } from '@/lib/project';
import {
  ContentHero,
  RelatedLinks,
} from '@/components/marketing/content-page';
import { ContentIndex } from '@/components/marketing/content-index';

export const metadata: Metadata = createPageMetadata({
  title: 'Blog',
  description:
    'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
  path: '/blog/',
});

const relatedLinks = [
  { href: '/vlr-gg-api/', label: 'VLR.gg API for Python' },
  { href: '/valorant-api-python/', label: 'Valorant API for Python' },
  { href: '/valorant-esports-api/', label: 'Valorant esports API' },
  { href: '/valorant-stats-api/', label: 'Valorant stats API' },
  { href: '/guides/', label: 'Guides' },
  { href: '/docs/', label: 'Documentation' },
];

export default function BlogPage() {
  const posts = getBlogEntries();

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Blog',
    // The `@id` is referenced by every post's `isPartOf`, so it has to resolve.
    '@id': `${canonicalUrl('/blog')}#blog`,
    name: `${project.name} Blog`,
    description:
      'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
    url: canonicalUrl('/blog'),
    inLanguage: 'en',
    publisher: { '@id': `${siteUrl}/#organization` },
    blogPost: posts.map((post) => ({
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.description,
      url: canonicalUrl(post.url),
      datePublished: toIsoDateTime(post.date),
    })),
  };

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />

      <ContentHero
        eyebrow="Resources / Blog"
        title={
          <>
            Notes on Valorant
            <br />
            <span className="text-fd-primary">esports data.</span>
          </>
        }
        description="News, tutorials, and deep dives on building with the VLRdevAPI Python SDK. Practical notes on typed models, coverage, and shipping without a scraper."
      >
        <Link
          href="/guides/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
        >
          Browse guides
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
        <Link
          href="/docs/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white/15 px-5 text-[13px] font-medium text-white/65 transition-colors hover:border-white/30 hover:text-white"
        >
          Read the docs
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      </ContentHero>

      <ContentIndex
        title="All posts"
        items={posts}
        basePath="/blog"
        itemNoun="post"
        actionLabel="Read post"
        emptyMessage="No posts yet."
      />

      <RelatedLinks links={relatedLinks} />
    </main>
  );
}
