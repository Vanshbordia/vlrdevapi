import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "VLRdevAPI Blog"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'News, tutorials, and deep dives'}
      description={'Everything the VLRdevAPI team has shipped: release notes, integration write-ups, and comparisons with the alternatives.'}
      eyebrow="Blog"
    />,
    { ...size }
  )
}
