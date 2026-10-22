import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "FAQ - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Frequently asked'}
      description={'Everything you need to know about the VLRdevAPI Python SDK, from installation to rate limits.'}
      eyebrow={"FAQ"}
    />,
    { ...size }
  )
}
