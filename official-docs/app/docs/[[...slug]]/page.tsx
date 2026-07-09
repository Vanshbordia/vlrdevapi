import { getPageImage, getPageMarkdownUrl, source } from '@/lib/source';
import {
  DocsBody,
  DocsDescription,
  DocsPage,
  DocsTitle,
  MarkdownCopyButton,
  PageLastUpdate,
  ViewOptionsPopover,
} from 'fumadocs-ui/layouts/docs/page';
import { notFound } from 'next/navigation';
import { getMDXComponents } from '@/components/mdx';
import type { Metadata } from 'next';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import { gitConfig } from '@/lib/shared';


export default async function Page(props: PageProps<'/docs/[[...slug]]'>) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();
  const lastModifiedTime = page.data.lastModified;

  const MDX = page.data.body;
  const markdownUrl = getPageMarkdownUrl(page).url;

  const pageUrl = `https://vlrdevapi.pages.dev${page.url}${page.url.endsWith('/') ? '' : '/'}`;

  const jsonLdArticle = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    headline: page.data.title,
    description: page.data.description,
    url: pageUrl,
    dateModified: page.data.lastModified?.toISOString() ?? new Date().toISOString(),
    author: [
      {
        '@type': 'Person',
        name: 'Vansh Bordia',
      },
      {
        '@type': 'Organization',
        name: 'RiftWatch',
        url: 'https://riftwatch.org',
      },
    ],
    publisher: {
      '@type': 'Organization',
      name: 'RiftWatch',
      url: 'https://riftwatch.org',
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': pageUrl,
    },
  };

  const breadcrumbItems = [
    { '@type': 'ListItem', position: 1, name: 'Docs', item: 'https://vlrdevapi.pages.dev/docs/' },
    ...(params.slug ?? []).map((segment, i) => ({
      '@type': 'ListItem' as const,
      position: i + 2,
      name: segment,
      item: `https://vlrdevapi.pages.dev/docs/${(params.slug ?? []).slice(0, i + 1).join('/')}/`,
    })),
  ];

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbItems,
  };

  return (
    <DocsPage toc={page.data.toc} full={page.data.full} tableOfContent={{ style: 'normal' }}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdArticle).replace(/</g, '\\u003c'),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdBreadcrumb).replace(/</g, '\\u003c'),
        }}
      />
      <DocsTitle>{page.data.title}</DocsTitle>
      <DocsDescription className="mb-0">{page.data.description}</DocsDescription>
      <div className="flex flex-row gap-2 items-center border-b pb-6">
        <MarkdownCopyButton markdownUrl={markdownUrl} />
        <ViewOptionsPopover
          markdownUrl={markdownUrl}
          githubUrl={`https://github.com/${gitConfig.user}/${gitConfig.repo}/blob/${gitConfig.branch}/official-docs/content/docs/${page.path}`}
        />
      </div>
      <DocsBody>
        <MDX
          components={getMDXComponents({
            // this allows you to link to other pages with relative file paths
            a: createRelativeLink(source, page),
          })}
        />
      </DocsBody>
      {lastModifiedTime && <PageLastUpdate date={lastModifiedTime} />}
    </DocsPage>
  );
}

export async function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata(props: PageProps<'/docs/[[...slug]]'>): Promise<Metadata> {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const ogUrl = `https://vlrdevapi.pages.dev${page.url}${page.url.endsWith('/') ? '' : '/'}`;

  return {
    title: page.data.title,
    description: page.data.description,
    openGraph: {
      url: ogUrl,
      images: getPageImage(page).url,
    },
  }
}
