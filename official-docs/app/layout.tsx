import { Provider } from '@/components/provider';
import type { Metadata } from 'next';
import './global.css';
import { Geist } from "next/font/google";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'),
  title: {
    default: 'VLRdevAPI - Python SDK for Valorant Esports Data (VLR.gg)',
    template: '%s | VLRdevAPI',
  },
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg. Fetch match results, player stats, team rosters, and tournament brackets through a fully typed Python interface. Built by RiftWatch.',
  keywords: [
    'Valorant esports API',
    'Python SDK',
    'VLR.gg API',
    'Valorant match data',
    'Valorant player statistics',
    'esports data pipeline',
    'Valorant tournament brackets',
    'Python Valorant API',
  ],
  openGraph: {
    title: 'VLRdevAPI - Python SDK for Valorant Esports Data',
    description:
      'Fetch live and historical Valorant esports data from VLR.gg with a clean, type-safe Python interface. Match results, player stats, team rosters, and tournament brackets.',
    siteName: 'VLRdevAPI by RiftWatch',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VLRdevAPI - Python SDK for Valorant Esports Data',
    description:
      'Fetch live and historical Valorant esports data from VLR.gg with a clean, type-safe Python interface.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

const jsonLdOrganization = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'RiftWatch',
  url: 'https://riftwatch.org',
  logo: 'https://vlrdevapi.pages.dev/logo.png',
};

const jsonLdWebSite = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'VLRdevAPI',
  url: 'https://vlrdevapi.pages.dev',
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg.',
  applicationCategory: 'DeveloperApplication',
  operatingSystem: 'Python 3.11+',
  author: {
    '@type': 'Organization',
    name: 'RiftWatch',
    url: 'https://riftwatch.org',
  },
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={geist.variable} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLdOrganization).replace(/</g, '\\u003c'),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLdWebSite).replace(/</g, '\\u003c'),
          }}
        />
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
