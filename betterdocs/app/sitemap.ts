import type { MetadataRoute } from 'next';

import { source } from '@/lib/source';

export const revalidate = false;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://vlrdevapi.pages.dev';
  const url = (path: string): string => new URL(path, baseUrl).toString();

  // Get all docs pages from fumadocs source
  const docsPages = source.getPages();

  const docsItems: MetadataRoute.Sitemap = docsPages.map((page) => {
    return {
      url: url(page.url),
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    };
  });

  return [
    // Home page
    {
      url: url('/'),
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 1,
    },
    // All docs pages (auto-generated from content)
    ...docsItems,
  ];
}
