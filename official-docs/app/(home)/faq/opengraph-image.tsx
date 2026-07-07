import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

export const alt = 'FAQ - VLRdevAPI'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function OGImage() {
  return new ImageResponse(
    <OGTemplate
      title="FAQ"
      description="Frequently asked questions about VLRdevAPI, the Python SDK for Valorant esports data"
    />,
    { ...size }
  )
}
