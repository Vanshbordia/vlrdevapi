import { getPageMarkdownUrl, source } from '@/lib/source';
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
import type { Metadata, ResolvingMetadata } from 'next';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import { canonicalUrl, gitConfig, siteUrl } from '@/lib/shared';
import { getOgImage, resolveOgImage } from '@/lib/seo';
import { project, projectAuthor } from '@/lib/project';
import { i18n } from '@/lib/i18n';

const OG_LOCALES: Record<string, string> = {
  'pt-br': 'pt_BR',
  es: 'es_ES',
  'zh-cn': 'zh_CN',
};

export default async function Page(props: {
  params: Promise<{ lang: string; slug?: string[] }>;
}) {
  const { lang, slug } = await props.params;
  if (!i18n.languages.includes(lang as any) || lang === i18n.defaultLanguage) {
    notFound();
  }

  const page = source.getPage(slug, lang);
  if (!page) notFound();
  const lastModifiedTime = page.data.lastModified;

  const MDX = page.data.body;
  const markdownUrl = getPageMarkdownUrl(page).url;

  const pageUrl = canonicalUrl(page.url);
  const ogImage = await getOgImage(page.url);

  const jsonLdArticle = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    '@id': `${pageUrl}#article`,
    mainEntityOfPage: { '@type': 'WebPage', '@id': pageUrl },
    headline: page.data.title,
    description: page.data.description,
    ...(ogImage ? { image: [ogImage] } : {}),
    url: pageUrl,
    dateModified: page.data.lastModified?.toISOString() ?? new Date().toISOString(),
    author: projectAuthor,
    publisher: { '@id': `${siteUrl}/#organization` },
    inLanguage: lang,
  };

  const segmentLabel = (segment: string) =>
    segment.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

  const breadcrumbItems = [
    { '@type': 'ListItem', position: 1, name: 'Docs', item: canonicalUrl(`/${lang}/docs`) },
    ...(slug ?? []).map((segment, i) => ({
      '@type': 'ListItem' as const,
      position: i + 2,
      name: segmentLabel(segment),
      item: canonicalUrl(`/${lang}/docs/${(slug ?? []).slice(0, i + 1).join('/')}`),
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
            a: createRelativeLink(source, page),
          })}
        />
      </DocsBody>
      {lastModifiedTime && <PageLastUpdate date={lastModifiedTime} />}
    </DocsPage>
  );
}

export async function generateStaticParams() {
  const nonDefaultLanguages = i18n.languages.filter((l) => l !== i18n.defaultLanguage);
  const params: { lang: string; slug?: string[] }[] = [];

  for (const lang of nonDefaultLanguages) {
    const pages = source.getPages(lang);
    for (const page of pages) {
      params.push({
        lang,
        slug: page.slugs,
      });
    }
  }

  return params;
}

export async function generateMetadata(
  props: { params: Promise<{ lang: string; slug?: string[] }> },
  parent: ResolvingMetadata
): Promise<Metadata> {
  const { lang, slug } = await props.params;
  const page = source.getPage(slug, lang);
  if (!page) notFound();

  await resolveOgImage(page.url, parent);

  const parentMetadata = await parent;
  const images = parentMetadata.openGraph?.images;

  const ogUrl = canonicalUrl(page.url);
  const title = page.data.title;
  const enPage = source.getPage(slug, 'en');

  return {
    title,
    description: page.data.description,
    alternates: {
      canonical: ogUrl,
      languages: {
        en: canonicalUrl(enPage?.url ?? '/docs'),
        'pt-BR': canonicalUrl(source.getPage(slug, 'pt-br')?.url ?? `/pt-br${enPage?.url ?? '/docs'}`),
        es: canonicalUrl(source.getPage(slug, 'es')?.url ?? `/es${enPage?.url ?? '/docs'}`),
        'zh-CN': canonicalUrl(source.getPage(slug, 'zh-cn')?.url ?? `/zh-cn${enPage?.url ?? '/docs'}`),
      },
    },
    openGraph: {
      type: 'article',
      siteName: project.name,
      locale: OG_LOCALES[lang] ?? 'en_US',
      url: ogUrl,
      title: `${title} | ${project.name}`,
      description: page.data.description,
      ...(images ? { images } : {}),
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} | ${project.name}`,
      description: page.data.description,
    },
  };
}
