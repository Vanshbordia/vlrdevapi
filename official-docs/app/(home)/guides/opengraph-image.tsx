import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

export const alt = 'Guides - VLRdevAPI'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function OGImage() {
  return new ImageResponse(
    <OGTemplate
      title="Guides"
      description="Step-by-step walkthroughs for integrating VLRdevAPI into your Valorant esports projects"
    />,
    { ...size }
  )
}
