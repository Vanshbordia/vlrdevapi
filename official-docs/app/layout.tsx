import { Analytics } from '@/components/analytics';
import { Provider } from '@/components/provider';
import type { Metadata } from 'next';
import './global.css';
import { Geist } from "next/font/google";
import { siteUrl } from '@/lib/shared';
import {
  project,
  projectAuthor,
  projectKeywords,
  projectPublisher,
  projectSameAs,
  projectUrls,
} from '@/lib/project';

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'VLRdevAPI - Python SDK for Valorant Esports Data (VLR.gg)',
    template: '%s | VLRdevAPI',
  },
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg. Fetch match results, player stats, team rosters, and tournament brackets through a fully typed Python interface.',
  keywords: projectKeywords,
  openGraph: {
    title: 'VLRdevAPI - Python SDK for Valorant Esports Data',
    description:
      'Fetch live and historical Valorant esports data from VLR.gg with a clean, type-safe Python interface. Match results, player stats, team rosters, and tournament brackets.',
    url: `${siteUrl}/`,
    siteName: 'VLRdevAPI',
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
  verification: {
    google: 'yVaBi-Tr3-OH7NnWQ8GPL1vbkqC_FOXAEQPlbSLKdsE',
    other: {
      // Bing Webmaster Tools.
      'msvalidate.01': 'C5DF5211F5F3C14452F41EFC044D7E89',
    },
  },
};

const jsonLdOrganization = {
  '@context': 'https://schema.org',
  '@id': `${siteUrl}/#organization`,
  ...projectPublisher,
};

const jsonLdWebSite = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  '@id': `${siteUrl}/#website`,
  name: project.name,
  alternateName: 'VLR.gg Python API',
  url: projectUrls.home,
  description: project.description,
  inLanguage: 'en',
  publisher: { '@id': `${siteUrl}/#organization` },
  author: projectAuthor,
  sameAs: projectSameAs,
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={geist.variable} suppressHydrationWarning>
      <Analytics />
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
