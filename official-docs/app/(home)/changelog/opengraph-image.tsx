import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

export const alt = 'Changelog - VLRdevAPI'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function OGImage() {
  return new ImageResponse(
    <OGTemplate
      title="Changelog"
      description="Release history and version notes for VLRdevAPI"
    />,
    { ...size }
  )
}
