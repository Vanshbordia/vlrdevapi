import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'
import { getBlogPost, getBlogPosts } from '@/lib/content'

export const alt = 'VLRdevAPI Blog'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export async function generateStaticParams() {
  return getBlogPosts().map((post) => ({ slug: post.slug }))
}

export default async function OGImage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = getBlogPost(slug)

  return new ImageResponse(
    <OGTemplate
      title={post?.title ?? 'Blog Post'}
      description={post?.description}
    />,
    { ...size }
  )
}
