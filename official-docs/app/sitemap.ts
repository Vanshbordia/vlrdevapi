import type { MetadataRoute } from 'next'
import { getBlogEntries, getGuideEntries, source } from '@/lib/source'
import { canonicalUrl } from '@/lib/shared'
import { latestChangelogDate } from '@/lib/changelog'

export const dynamic = 'force-static'

/**
 * Marketing routes that are not part of a content collection. Kept as a single
 * list so the sitemap, the header and the footer cannot drift apart.
 */
export const MARKETING_ROUTES: Array<{
  path: string
  changeFrequency: 'daily' | 'weekly' | 'monthly' | 'yearly'
  priority: number
}> = [
  { path: '/blog/', changeFrequency: 'weekly', priority: 0.8 },
  { path: '/guides/', changeFrequency: 'weekly', priority: 0.8 },
  { path: '/vlr-gg-api/', changeFrequency: 'monthly', priority: 0.9 },
  { path: '/valorant-esports-api/', changeFrequency: 'monthly', priority: 0.9 },
  { path: '/valorant-api-python/', changeFrequency: 'monthly', priority: 0.9 },
  { path: '/valorant-stats-api/', changeFrequency: 'monthly', priority: 0.9 },
  { path: '/changelog/', changeFrequency: 'monthly', priority: 0.7 },
  { path: '/faq/', changeFrequency: 'monthly', priority: 0.6 },
]

export default function sitemap(): MetadataRoute.Sitemap {
  const docUrls = source.getPages().map((page) => ({
    url: canonicalUrl(page.url),
    lastModified: page.data.lastModified,
    changeFrequency: 'weekly' as const,
    priority: page.url === '/docs' ? 1 : 0.8,
  }))

  const blogUrls = getBlogEntries().map((post) => ({
    url: canonicalUrl(post.url),
    lastModified: post.lastModified ?? new Date(post.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const guideUrls = getGuideEntries().map((guide) => ({
    url: canonicalUrl(guide.url),
    lastModified: guide.lastModified ?? new Date(guide.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const marketingUrls = MARKETING_ROUTES.map((route) => ({
    url: canonicalUrl(route.path),
    // The changelog carries a real release date; every other marketing page is
    // static, so it deliberately has no `lastModified` (a build timestamp
    // would make the sitemap churn on every deploy).
    lastModified: route.path === '/changelog' ? latestChangelogDate : undefined,
    changeFrequency: route.changeFrequency,
    priority: route.priority,
  }))

  return [
    {
      url: canonicalUrl('/'),
      changeFrequency: 'weekly' as const,
      priority: 1,
    },
    ...marketingUrls,
    ...blogUrls,
    ...guideUrls,
    ...docUrls,
  ]
}
