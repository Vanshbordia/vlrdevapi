import { source } from '@/lib/source';
import { getBlogPosts, getGuides } from '@/lib/content';
import { llms } from 'fumadocs-core/source';

export const revalidate = false;

const BASE_URL = 'https://vlrdevapi.pages.dev';

function linkSection(
  heading: string,
  kind: 'blog' | 'guides',
  items: { slug: string; title: string; description: string }[],
) {
  const lines = items.map((item) => {
    const html = `${BASE_URL}/${kind}/${item.slug}/`;
    const markdown = `${BASE_URL}/llms.mdx/${kind}/${item.slug}/content.md`;
    return `- [${item.title}](${html}): ${item.description} ([markdown](${markdown}))`;
  });

  return `## ${heading}\n\n${lines.join('\n')}`;
}

const faq = `## FAQ

**What is VLRdevAPI?** VLRdevAPI is a Python library for accessing VLR.gg Valorant esports data. It returns typed Pydantic models and needs no API key.

**Do I need an API key?** No. Install the package and start calling methods.

**What Python version is required?** Python 3.11 or newer.

**What data can it return?** Upcoming, live, and completed matches; team info, rosters, stats, placements, and transactions; player info, agent stats, match history, and profiles; event listings, stages, teams, matches, and standings; series info, VODs, player stats, rounds, performance, and economy; and news listings plus full articles.

**How is it installed?** \`pip install vlrdevapi\` or \`uv add vlrdevapi\`.

**Where is the full reference?** ${BASE_URL}/docs`;

export function GET() {
  // Blog and guides are separate MDX collections, so they are not part of the
  // docs page tree that llms(source).index() walks. Add them explicitly.
  const blog = getBlogPosts().map((post) => ({
    slug: post.slug,
    title: post.title,
    description: post.description,
  }));
  const guides = getGuides().map((guide) => ({
    slug: guide.slug,
    title: guide.title,
    description: guide.description,
  }));

  const sections = [llms(source).index()];

  if (blog.length) sections.push(linkSection('Blog', 'blog', blog));
  if (guides.length) sections.push(linkSection('Guides', 'guides', guides));

  sections.push(faq);

  return new Response(sections.join('\n\n'));
}
