import { getLLMTextFor, guidesSource } from '@/lib/source';
import { notFound } from 'next/navigation';

export const dynamic = 'force-static';

export async function GET(
  _req: Request,
  { params }: RouteContext<'/llms.mdx/guides/[[...slug]]'>,
) {
  const { slug } = await params;
  // The last segment is always "content.md" (see generateStaticParams).
  const page = guidesSource.getPage(slug?.slice(0, -1));
  if (!page) notFound();

  return new Response(await getLLMTextFor(page), {
    headers: {
      'Content-Type': 'text/markdown',
    },
  });
}

export function generateStaticParams() {
  return guidesSource.getPages().map((page) => ({
    slug: [...page.slugs, 'content.md'],
  }));
}
