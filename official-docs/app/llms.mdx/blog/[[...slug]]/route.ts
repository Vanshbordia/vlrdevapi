import { blogSource, getLLMTextFor } from '@/lib/source';
import { notFound } from 'next/navigation';

export const dynamic = 'force-static';

export async function GET(
  _req: Request,
  { params }: RouteContext<'/llms.mdx/blog/[[...slug]]'>,
) {
  const { slug } = await params;
  // The last segment is always "content.md" (see generateStaticParams).
  const page = blogSource.getPage(slug?.slice(0, -1));
  if (!page) notFound();

  return new Response(await getLLMTextFor(page), {
    headers: {
      'Content-Type': 'text/markdown',
    },
  });
}

export function generateStaticParams() {
  return blogSource.getPages().map((page) => ({
    slug: [...page.slugs, 'content.md'],
  }));
}
