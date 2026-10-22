import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = "Changelog - VLRdevAPI"
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Every release. Every fix.'}
      description={'The full release history of VLRdevAPI - new namespaces, model changes, and parser fixes.'}
      eyebrow={"Changelog"}
    />,
    { ...size }
  )
}
