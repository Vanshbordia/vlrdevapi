import type { MetadataRoute } from 'next'
import { source } from '@/lib/source'
import { getBlogPosts, getGuides } from '@/lib/content'
import { siteUrl } from '@/lib/shared'

export const dynamic = 'force-static'

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = source.getPages()

  const docUrls = pages.map((page) => ({
    url: `${siteUrl}${page.url}${page.url.endsWith('/') ? '' : '/'}`,
    lastModified: page.data.lastModified ?? new Date(),
    changeFrequency: 'weekly' as const,
    priority: page.url === '/docs' ? 1 : 0.8,
  }))

  const blogPosts = getBlogPosts()
  const guideItems = getGuides()

  const blogUrls = blogPosts.map((post) => ({
    url: `${siteUrl}/blog/${post.slug}/`,
    lastModified: new Date(post.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const guideUrls = guideItems.map((guide) => ({
    url: `${siteUrl}/guides/${guide.slug}/`,
    lastModified: new Date(guide.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  return [
    {
      url: siteUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${siteUrl}/blog/`,
      lastModified: blogPosts.length > 0 ? new Date(blogPosts[0].date) : new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${siteUrl}/guides/`,
      lastModified: guideItems.length > 0 ? new Date(guideItems[0].date) : new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${siteUrl}/vlr-gg-api/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.9,
    },
    {
      url: `${siteUrl}/valorant-esports-api/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.9,
    },
    {
      url: `${siteUrl}/valorant-api-python/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.9,
    },
    {
      url: `${siteUrl}/valorant-stats-api/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.9,
    },
    {
      url: `${siteUrl}/changelog/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${siteUrl}/faq/`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    ...blogUrls,
    ...guideUrls,
    ...docUrls,
  ]
}
