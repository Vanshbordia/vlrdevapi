import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'
import { blogSource } from '@/lib/source'

// Image metadata
export const alt = "VLRdevAPI Blog"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

// `output: 'export'` requires every dynamic route to enumerate its params.
export function generateStaticParams() {
  return blogSource.getPages().map((page) => ({ slug: page.slugs[0] }))
}

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const entry = blogSource.getPage([slug])

  return new ImageResponse(
    <OGTemplate
      title={entry?.data.title ?? 'Blog post'}
      description={entry?.data.description}
      eyebrow="Blog"
    />,
    { ...size }
  )
}
