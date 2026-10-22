import { ImageResponse } from 'next/og'
import { OGTemplate } from '@/components/og-template'

// Image metadata
export const alt = 'VLRdevAPI Documentation'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const dynamic = 'force-static'

/**
 * Social card for the documentation section.
 *
 * The docs pages live behind an optional catch-all (`app/docs/[[...slug]]`),
 * and a catch-all segment has to be the last part of a URL. A per-page
 * `opengraph-image` file inside that segment would therefore never become a
 * route. The card lives one level up, in the `/docs` segment, and is inherited
 * by every documentation page.
 */
export default function Image() {
  return new ImageResponse(
    <OGTemplate
      title={'Documentation'}
      description={'Guides, API references, and examples for the VLRdevAPI Python SDK and REST API.'}
      eyebrow="Docs"
    />,
    { ...size }
  )
}
