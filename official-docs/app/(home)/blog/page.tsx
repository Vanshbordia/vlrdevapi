import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { getBlogPosts } from '@/lib/content';
import { JsonLd } from '@/components/json-ld';
import { canonicalUrl, siteUrl } from '@/lib/shared';
import { createPageMetadata } from '@/lib/seo';
import { project } from '@/lib/project';
import {
  ContentCard,
  ContentHero,
  RelatedLinks,
} from '@/components/marketing/content-page';

export const metadata: Metadata = createPageMetadata({
  title: 'Blog',
  description:
    'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
  path: '/blog/',
  openGraph: { title: 'VLRdevAPI Blog - News, Tutorials, and Deep Dives' },
  twitter: { title: 'VLRdevAPI Blog - News, Tutorials, and Deep Dives' },
});

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Blog',
  name: `${project.name} Blog`,
  description: 'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
  url: canonicalUrl('/blog/'),
  inLanguage: 'en',
  publisher: { '@id': `${siteUrl}/#organization` },
};

const relatedLinks = [
  { href: '/vlr-gg-api/', label: 'VLR.gg API for Python' },
  { href: '/valorant-api-python/', label: 'Valorant API for Python' },
  { href: '/valorant-esports-api/', label: 'Valorant esports API' },
  { href: '/valorant-stats-api/', label: 'Valorant stats API' },
  { href: '/guides/', label: 'Guides' },
  { href: '/docs/', label: 'Documentation' },
];

export default function BlogPage() {
  const posts = getBlogPosts();

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />

      <ContentHero
        eyebrow="Resources / Blog"
        title={
          <>
            Notes from the
            <br />
            <span className="text-[#ff4655]">data layer.</span>
          </>
        }
        description="News, tutorials, and deep dives on building with the VLRdevAPI Python SDK. Practical notes on Valorant esports data, typed models, and shipping with less scraping."
      >
        <Link
          href="/guides/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
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

      <section>
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-4">
            <div>
              <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
                The index
              </p>
              <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
                All posts
              </h2>
            </div>
            <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
              {posts.length} {posts.length === 1 ? 'post' : 'posts'}
            </span>
          </div>

          {posts.length === 0 ? (
            <p className="mt-8 border border-white/10 bg-white/[0.02] p-5 text-[13px] text-white/40">
              No posts yet.
            </p>
          ) : (
            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              {posts.map((post, index) => (
                <ContentCard
                  key={post.slug}
                  href={`/blog/${post.slug}/`}
                  index={String(index + 1).padStart(2, '0')}
                  date={post.date}
                  title={post.title}
                  description={post.description}
                  actionLabel="Read post"
                />
              ))}
            </div>
          )}
        </div>
      </section>

      <RelatedLinks links={relatedLinks} />
    </main>
  );
}
