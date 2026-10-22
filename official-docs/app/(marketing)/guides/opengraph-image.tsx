import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "VLRdevAPI Guides"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Guides for Python developers'}
      description={'Step-by-step walkthroughs for Discord bots, live monitors, pandas notebooks, and Polars pipelines.'}
      eyebrow={"Guides"}
    />,
    { ...size }
  )
}
