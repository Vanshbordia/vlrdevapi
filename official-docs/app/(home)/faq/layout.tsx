import type { Metadata } from 'next'
import { canonicalUrl } from '@/lib/shared'

export const metadata: Metadata = {
  title: 'FAQ',
  description:
    'Frequently asked questions about VLRdevAPI, the type-safe Python SDK for Valorant esports data from VLR.gg.',
  alternates: { canonical: canonicalUrl('/faq/') },
}

export default function FaqLayout({ children }: { children: React.ReactNode }) {
  return children
}
