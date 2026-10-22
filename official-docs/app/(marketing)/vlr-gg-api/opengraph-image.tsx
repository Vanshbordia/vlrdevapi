import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "VLR.gg API for Python (Unofficial) - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'VLR.gg API for Python'}
      description={'An unofficial, type-safe Python client for VLR.gg esports data. No API key, no parser.'}
      eyebrow={"Python SDK"}
    />,
    { ...size }
  )
}
