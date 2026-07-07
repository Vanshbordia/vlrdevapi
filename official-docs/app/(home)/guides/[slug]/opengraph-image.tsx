import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'
import { getGuide, getGuides } from '@/lib/content'

export const alt = 'VLRdevAPI Guides'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export async function generateStaticParams() {
  return getGuides().map((guide) => ({ slug: guide.slug }))
}

export default async function OGImage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const guide = getGuide(slug)

  return new ImageResponse(
    <OGTemplate
      title={guide?.title ?? 'Guide'}
      description={guide?.description}
    />,
    { ...size }
  )
}
