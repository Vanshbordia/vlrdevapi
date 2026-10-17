import { blogSource, getLLMTextFor, guidesSource, source } from '@/lib/source';

export const revalidate = false;

export async function GET() {
  // Docs, blog, and guides are separate collections. getLLMTextFor renders each
  // page as markdown, so include all three in the full dump.
  const pages = [
    ...source.getPages(),
    ...blogSource.getPages(),
    ...guidesSource.getPages(),
  ];

  const scanned = await Promise.all(pages.map((page) => getLLMTextFor(page)));

  return new Response(scanned.join('\n\n'));
}
