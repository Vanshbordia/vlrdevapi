import { getPageMarkdownUrl, source } from '@/lib/source';
import { getBlogPosts, getGuides } from '@/lib/content';
import { llms } from 'fumadocs-core/source';

export const revalidate = false;

const BASE_URL = 'https://vlrdevapi.pages.dev';

const summary = `# VLRdevAPI

> A type-safe Python SDK for Valorant esports data from VLR.gg. It returns typed Pydantic models for matches, players, teams, events, series, and news.

- **What it is**: an open-source Python client that reads VLR.gg and returns typed objects, so you do not have to write or maintain a scraper.
- **When to use it**: you need Valorant esports data in Python, including upcoming and live matches, results, standings, team rosters, player statistics, or news.
- **Key endpoints**: \`vlrdevapi.matches.upcoming()\`, \`vlrdevapi.matches.live()\`, \`vlrdevapi.player(id).profile()\`, \`vlrdevapi.team(id).info()\`, \`vlrdevapi.event(id).info()\`, \`vlrdevapi.series(id).info()\`, and \`vlrdevapi.news()\`.
- **Install**: \`pip install vlrdevapi\` or \`uv add vlrdevapi\`, on Python 3.11 or newer.
- **Free and no API key**: no key, token, subscription, or account is required.`;

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

const useCases = `## Use cases

- [VLR.gg API for Python](${BASE_URL}/vlr-gg-api/): Why an unofficial Python client exists for VLR.gg, and what it fetches.
- [Valorant esports API](${BASE_URL}/valorant-esports-api/): Query Valorant esports data from VLR.gg in Python.
- [Valorant API for Python](${BASE_URL}/valorant-api-python/): Install the Python client and work with typed models.
- [Valorant stats API](${BASE_URL}/valorant-stats-api/): Player, team, and match statistics from VLR.gg in Python.`;

/**
 * Fumadocs renders the docs index as `- [Title](url): description`. Append a
 * link to the per-page markdown so LLMs can fetch the raw source, the same way
 * the Blog and Guides sections do. The docs heading is demoted to `##` because
 * the summary block owns the single `#` heading.
 */
function withDocMarkdownLinks(index: string) {
  const markdownByUrl = new Map<string, string>();
  for (const page of source.getPages()) {
    markdownByUrl.set(page.url, `${BASE_URL}${getPageMarkdownUrl(page).url}`);
  }

  return index
    .split('\n')
    .map((line) => {
      const match = line.match(/\]\((\/[^)]*)\)/);
      const markdown = match ? markdownByUrl.get(match[1]) : undefined;
      return markdown ? `${line} ([markdown](${markdown}))` : line;
    })
    .join('\n')
    .replace(/^# /, '## ');
}

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

  const sections = [summary, withDocMarkdownLinks(llms(source).index() as string)];

  if (blog.length) sections.push(linkSection('Blog', 'blog', blog));
  if (guides.length) sections.push(linkSection('Guides', 'guides', guides));

  sections.push(useCases);
  sections.push(faq);

  return new Response(sections.join('\n\n'));
}
