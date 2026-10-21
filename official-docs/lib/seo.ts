import type { Metadata } from 'next';
import { canonicalUrl } from './shared';

type OpenGraphMetadata = NonNullable<Metadata['openGraph']>;
type TwitterMetadata = NonNullable<Metadata['twitter']>;

interface PageMetadataOptions {
  title: string;
  description: string;
  path: string;
  type?: 'website' | 'article';
  keywords?: string[];
  openGraph?: OpenGraphMetadata;
  twitter?: TwitterMetadata;
}

/**
 * Build page metadata with a consistent canonical URL, Open Graph payload, and
 * Twitter card. Individual pages can override any Open Graph or Twitter field.
 */
export function createPageMetadata({
  title,
  description,
  path,
  type = 'website',
  keywords,
  openGraph,
  twitter,
}: PageMetadataOptions): Metadata {
  const url = canonicalUrl(path);

  return {
    title,
    description,
    ...(keywords?.length ? { keywords } : {}),
    alternates: { canonical: url },
    openGraph: {
      title,
      description,
      url,
      siteName: 'VLRdevAPI',
      type,
      ...openGraph,
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      ...twitter,
    },
  };
}
