import { getLLMText, getPageMarkdownUrl, source } from '@/lib/source';
import { i18n } from '@/lib/i18n';
import { notFound } from 'next/navigation';

export const dynamic = 'force-static';

export async function GET(_req: Request, { params }: RouteContext<'/llms.mdx/docs/[[...slug]]'>) {
  const { slug } = await params;
  if (!slug || slug.length === 0) notFound();

  // remove the appended "content.md"
  const rawSegments = slug.slice(0, -1);
  const first = rawSegments[0];
  const isNonDefaultLang = i18n.languages.includes(first as any) && first !== i18n.defaultLanguage;
  const lang = isNonDefaultLang ? first : i18n.defaultLanguage;
  const pageSlugs = isNonDefaultLang ? rawSegments.slice(1) : rawSegments;

  const page = source.getPage(pageSlugs, lang);
  if (!page) notFound();

  return new Response(await getLLMText(page), {
    headers: {
      'Content-Type': 'text/markdown',
    },
  });
}

export function generateStaticParams() {
  return source.getPages().map((page) => ({
    slug: getPageMarkdownUrl(page).segments,
  }));
}
