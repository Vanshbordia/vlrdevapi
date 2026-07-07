import type { MetadataRoute } from 'next'
import { source } from '@/lib/source'
import { getBlogPosts, getGuides } from '@/lib/content'

export const dynamic = 'force-static'

const BASE_URL = 'https://vlrdevapi.pages.dev'

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = source.getPages()

  const docUrls = pages.map((page) => ({
    url: `${BASE_URL}${page.url}`,
    lastModified: page.data.lastModified ?? new Date(),
    changeFrequency: 'weekly' as const,
    priority: page.url === '/docs' ? 1 : 0.8,
  }))

  const blogPosts = getBlogPosts()
  const guideItems = getGuides()

  const blogUrls = blogPosts.map((post) => ({
    url: `${BASE_URL}/blog/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const guideUrls = guideItems.map((guide) => ({
    url: `${BASE_URL}/guides/${guide.slug}`,
    lastModified: new Date(guide.date),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${BASE_URL}/blog`,
      lastModified: blogPosts.length > 0 ? new Date(blogPosts[0].date) : new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/guides`,
      lastModified: guideItems.length > 0 ? new Date(guideItems[0].date) : new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/changelog`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/faq`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    ...blogUrls,
    ...guideUrls,
    ...docUrls,
  ]
}
