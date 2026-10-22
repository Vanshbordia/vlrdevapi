import type { Metadata } from 'next'

import ChangelogTimeline from './changelog-timeline'
import { JsonLd } from '@/components/json-ld'
import { canonicalUrl, siteUrl } from '@/lib/shared'
import { createPageMetadata } from '@/lib/seo'
import { project, projectAuthor, projectUrls } from '@/lib/project'
import { versions } from '@/lib/changelog'
import { ContentHero, IndexPanel, formatDate } from '@/components/marketing/content-page'

export const metadata: Metadata = createPageMetadata({
  title: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
  path: '/changelog/',})

const jsonLdBreadcrumb = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: projectUrls.home },
    { '@type': 'ListItem', position: 2, name: 'Changelog', item: canonicalUrl('/changelog') },
  ],
}

const jsonLdWebPage = {
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  name: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
  url: canonicalUrl('/changelog'),
  inLanguage: 'en',
  isPartOf: {
    '@type': 'WebSite',
    '@id': `${siteUrl}/#website`,
  },
  publisher: { '@id': `${siteUrl}/#organization` },
  about: {
    '@type': 'SoftwareSourceCode',
    name: project.name,
    programmingLanguage: project.programmingLanguage,
    runtimePlatform: project.runtimePlatform,
    codeRepository: project.repositoryUrl,
    license: project.licenseUrl,
    author: projectAuthor,
  },
}

export default function ChangelogPage() {
  const latest = versions[0]

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLdBreadcrumb} />
      <JsonLd data={jsonLdWebPage} />
      <ContentHero
        eyebrow="Project / Changelog"
        title={
          <>
            Every release.
            <br />
            <span className="text-fd-primary">Every fix.</span>
          </>
        }
        description="Track the full release history of VLRdevAPI. New namespaces, model changes, parser fixes, and everything that moves the SDK forward."
        aside={
          <IndexPanel
            label="Release index"
            rows={[
              { label: 'Releases', value: String(versions.length).padStart(2, '0') },
              { label: 'Latest', value: `v${latest.version}` },
              { label: 'Published', value: latest ? formatDate(latest.date) : '—' },
              { label: 'Channel', value: 'PyPI / GitHub' },
            ]}
            note="Version notes are ordered newest first."
          />
        }
      />

      <section>
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <ChangelogTimeline versions={versions} />
        </div>
      </section>
    </main>
  )
}
