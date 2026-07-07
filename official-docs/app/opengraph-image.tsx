import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

export const alt = 'VLRdevAPI'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function OGImage() {
  return new ImageResponse(
    <OGTemplate
      title="A Python SDK for Valorant Esports Data"
      description="Fetch match results, player stats, team rosters, and tournament brackets from VLR.gg"
    />,
    { ...size }
  )
}
