import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "Valorant API for Python (No API Key) - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Valorant API for Python'}
      description={'Install from PyPI and query VLR.gg Valorant esports data with typed Pydantic models.'}
      eyebrow={"Python SDK"}
    />,
    { ...size }
  )
}
