import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { getGuides } from '@/lib/content';
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
  title: 'Guides',
  description:
    'Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects.',
  path: '/guides/',
  openGraph: { title: 'VLRdevAPI Guides - Python SDK Walkthroughs' },
  twitter: { title: 'VLRdevAPI Guides - Python SDK Walkthroughs' },
});

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'CollectionPage',
  name: `${project.name} Guides`,
  description: 'Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects.',
  url: canonicalUrl('/guides/'),
  inLanguage: 'en',
  publisher: { '@id': `${siteUrl}/#organization` },
};

const relatedLinks = [
  { href: '/vlr-gg-api/', label: 'VLR.gg API for Python' },
  { href: '/valorant-esports-api/', label: 'Valorant esports API' },
  { href: '/valorant-stats-api/', label: 'Valorant stats API' },
  { href: '/docs/', label: 'Documentation' },
  { href: '/blog/', label: 'Blog' },
  { href: '/faq/', label: 'FAQ' },
];

export default function GuidesPage() {
  const guides = getGuides();

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />

      <ContentHero
        eyebrow="Resources / Guides"
        title={
          <>
            Guides for the
            <br />
            <span className="text-[#ff4655]">data layer.</span>
          </>
        }
        description="Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects. Every guide is built around real VLR.gg data and typed Python output."
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
          href="/blog/"
          className="group inline-flex h-11 items-center gap-1.5 border border-white/15 px-5 text-[13px] font-medium text-white/65 transition-colors hover:border-white/30 hover:text-white"
        >
          Browse the blog
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
                All guides
              </h2>
            </div>
            <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
              {guides.length} {guides.length === 1 ? 'entry' : 'entries'}
            </span>
          </div>

          {guides.length === 0 ? (
            <p className="mt-8 border border-white/10 bg-white/[0.02] p-5 text-[13px] text-white/40">
              No guides yet.
            </p>
          ) : (
            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {guides.map((guide, index) => (
                <ContentCard
                  key={guide.slug}
                  href={`/guides/${guide.slug}/`}
                  index={String(index + 1).padStart(2, '0')}
                  date={guide.date}
                  title={guide.title}
                  description={guide.description}
                  actionLabel="Read guide"
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
