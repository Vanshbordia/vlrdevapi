import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "Valorant esports API - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Valorant esports API'}
      description={'VCT matches, events, stages, brackets, and standings for Valorant esports in Python.'}
      eyebrow={"Python SDK"}
    />,
    { ...size }
  )
}
