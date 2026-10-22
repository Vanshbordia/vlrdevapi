import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { getGuideEntries } from '@/lib/source';
import { JsonLd } from '@/components/json-ld';
import { canonicalUrl, siteUrl } from '@/lib/shared';
import { createPageMetadata } from '@/lib/seo';
import { project } from '@/lib/project';
import {
  ContentHero,
  RelatedLinks,
} from '@/components/marketing/content-page';
import { ContentIndex } from '@/components/marketing/content-index';

export const metadata: Metadata = createPageMetadata({
  title: 'Guides',
  description:
    'Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects.',
  path: '/guides/',
});

const relatedLinks = [
  { href: '/vlr-gg-api', label: 'VLR.gg API for Python' },
  { href: '/valorant-api-python', label: 'Valorant API for Python' },
  { href: '/valorant-esports-api', label: 'Valorant esports API' },
  { href: '/valorant-stats-api', label: 'Valorant stats API' },
  { href: '/docs', label: 'Documentation' },
  { href: '/blog', label: 'Blog' },
  { href: '/faq', label: 'FAQ' },
];

export default function GuidesPage() {
  const guides = getGuideEntries();

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    // Referenced by every guide's `isPartOf`, so it has to resolve.
    '@id': `${canonicalUrl('/guides')}#collection`,
    name: `${project.name} Guides`,
    description:
      'Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects.',
    url: canonicalUrl('/guides'),
    inLanguage: 'en',
    publisher: { '@id': `${siteUrl}/#organization` },
    hasPart: guides.map((guide) => ({
      '@type': 'TechArticle',
      '@id': `${canonicalUrl(guide.url)}#article`,
      url: canonicalUrl(guide.url),
      name: guide.title,
    })),
  };

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />

      <ContentHero
        eyebrow="Resources / Guides"
        title={
          <>
            Guides for
            <br />
            <span className="text-fd-primary">Python developers.</span>
          </>
        }
        description="Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects. Every guide is built around real VLR.gg data and typed Python output."
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

      <ContentIndex
        title="All guides"
        items={guides}
        basePath="/guides"
        itemNoun="entry"
        itemNounPlural="entries"
        actionLabel="Read guide"
        emptyMessage="No guides yet."
        columns="three"
      />

      <RelatedLinks links={relatedLinks} />
    </main>
  );
}
