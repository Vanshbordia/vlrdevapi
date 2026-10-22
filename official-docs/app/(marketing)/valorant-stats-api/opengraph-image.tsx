import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "Valorant stats API - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Valorant stats API'}
      description={'Player, team, series, and match statistics for Valorant esports, ready to analyze.'}
      eyebrow={"Python SDK"}
    />,
    { ...size }
  )
}
