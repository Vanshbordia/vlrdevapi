import { Analytics } from '@/components/analytics';
import { JsonLd } from '@/components/json-ld';
import { Provider } from '@/components/provider';
import type { Metadata } from 'next';
import './global.css';
import { Geist, JetBrains_Mono } from 'next/font/google';
import { siteUrl } from '@/lib/shared';
import {
  project,
  projectAuthor,
  projectKeywords,
  projectPublisher,
  projectSameAs,
  projectUrls,
} from '@/lib/project';

const geist = Geist({
  subsets: ['latin'],
  variable: '--font-geist',
  display: 'swap',
});

// `next/font` reserves `--font-mono` internally for fallback metric
// adjustments, so the family is exposed under a distinct name and mapped
// into the `--font-mono` theme key in `app/global.css`.
const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

/**
 * Site-wide metadata.
 *
 * Pages inherit these defaults and override only what differs. Note that
 * Next replaces `openGraph` and `twitter` wholesale when a page defines
 * them, so every page that overrides them has to restate `siteName`, `type`
 * and the card title (see `lib/seo.ts` for the shared builder).
 */
export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'VLRdevAPI - Python SDK for Valorant Esports Data',
    template: '%s | VLRdevAPI',
  },
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg. Fetch live match results, player stats, team rosters, and tournament brackets through a fully typed Python interface with no API key.',
  applicationName: project.name,
  authors: [{ name: project.author, url: project.githubProfileUrl }],
  creator: project.author,
  publisher: project.name,
  keywords: projectKeywords,
  openGraph: {
    type: 'website',
    siteName: project.name,
    locale: 'en_US',
    url: `${siteUrl}/`,
    title: 'VLRdevAPI - Python SDK for Valorant Esports Data',
    description:
      'Fetch live and historical Valorant esports data from VLR.gg with a clean, type-safe Python interface. Matches, players, teams, brackets, and round stats with zero API keys required.',
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
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
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
  alternateName: ['VLR.gg Python API', 'vlr api', 'VLRdevAPI SDK'],
  url: projectUrls.home,
  description: project.description,
  inLanguage: 'en',
  publisher: { '@id': `${siteUrl}/#organization` },
  author: projectAuthor,
  sameAs: projectSameAs,
};

/**
 * The product entity. One `SoftwareApplication` node for the whole site, so
 * search engines can tie every page back to a single product.
 */
const jsonLdSoftwareApp = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  '@id': `${siteUrl}/#software`,
  name: project.name,
  url: projectUrls.home,
  description: project.description,
  applicationCategory: 'DeveloperApplication',
  applicationSubCategory: 'Esports data SDK',
  operatingSystem: 'Windows, macOS, Linux',
  runtimePlatform: project.runtimePlatform,
  programmingLanguage: project.programmingLanguage,
  softwareVersion: project.version,
  codeRepository: project.repositoryUrl,
  license: project.licenseUrl,
  isAccessibleForFree: true,
  softwareHelp: projectUrls.docs,
  downloadUrl: project.packageUrl,
  image: projectUrls.logo,
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  author: projectAuthor,
  publisher: { '@id': `${siteUrl}/#organization` },
  sameAs: projectSameAs,
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html
      lang="en"
      className={`${geist.variable} ${mono.variable}`}
      suppressHydrationWarning
    >
      <body className="flex flex-col min-h-screen">
        <JsonLd data={jsonLdOrganization} />
        <JsonLd data={jsonLdWebSite} />
        <JsonLd data={jsonLdSoftwareApp} />
        <Provider>{children}</Provider>
        <Analytics />
      </body>
    </html>
  );
}
