import { getPageMarkdownUrl, getBlogEntries, getGuideEntries, source } from '@/lib/source';
import { llms } from 'fumadocs-core/source';
import { siteUrl } from '@/lib/shared';

export const dynamic = 'force-static';

const BASE_URL = siteUrl;

const summary = `# VLRdevAPI

> A type-safe Python SDK and Model Context Protocol (MCP) server for Valorant esports data from VLR.gg. It returns typed Pydantic models for matches, players, teams, events, series, and news, and supports universal tabular exports to pandas, Polars, CSV, Parquet, and Excel.

- **What it is**: an open-source Python client and MCP server that reads VLR.gg and returns typed objects, so you do not have to write or maintain a scraper.
- **When to use it**: you need Valorant esports data in Python, in AI agent workflows (Claude Desktop, Cursor), or exported into DataFrames/spreadsheets.
- **Key endpoints**: \`vlrdevapi.matches.upcoming()\`, \`vlrdevapi.matches.live()\`, \`vlrdevapi.player(id).profile()\`, \`vlrdevapi.team(id).info()\`, \`vlrdevapi.event(id).info()\`, \`vlrdevapi.series(id).info()\`, and \`vlrdevapi.news()\`.
- **Tabular exports**: every model supports \`.to_df()\`, \`.to_polars()\`, \`.to_csv()\`, \`.to_parquet()\`, \`.to_excel()\`, \`.to_json()\`, and \`.to_markdown()\`.
- **MCP Server**: built-in Model Context Protocol server CLI \`vlrdevapi-mcp\` exposing 41 tools for AI assistants.
- **Install**: \`pip install vlrdevapi\` (or \`pip install "vlrdevapi[all]"\`), on Python 3.11 or newer.
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

**What is VLRdevAPI?** VLRdevAPI is a type-safe Python library and Model Context Protocol (MCP) server for accessing VLR.gg Valorant esports data. It returns typed Pydantic models, supports universal tabular exports (pandas, Polars, CSV, Parquet, Excel), and needs no API key.

**How does the MCP server work?** Run \`vlrdevapi-mcp\` to start a stdio MCP server exposing 41 tools for Claude Desktop, Cursor, Zed, and AI agents.

**Do I need an API key?** No. Install the package and start calling methods.

**What Python version is required?** Python 3.11 or newer (Python 3.11–3.15 supported).

**What data can it return?** Upcoming, live, and completed matches; team info, rosters, stats, placements, and transactions; player info, agent stats, match history, and profiles; event listings, stages, teams, matches, and standings; series info, VODs, player stats, rounds, performance, and economy; and news listings plus full articles.

**How is it installed?** \`pip install vlrdevapi\` or \`pip install "vlrdevapi[all]"\`.

**Where is the full reference?** ${BASE_URL}/docs/`;

const useCases = `## Use cases

- [VLR.gg API for Python](${BASE_URL}/vlr-gg-api/): Why an unofficial Python client exists for VLR.gg, and what it fetches.
- [Valorant esports API](${BASE_URL}/valorant-esports-api/): Query Valorant esports data from VLR.gg in Python.
- [Valorant API for Python](${BASE_URL}/valorant-api-python/): Install the Python client and work with typed models.
- [Valorant stats API](${BASE_URL}/valorant-stats-api/): Player, team, and match statistics from VLR.gg in Python.`;

/**
 * Fumadocs renders the docs index as \`- [Title](url): description\`. Append a
 * link to the per-page markdown so LLMs can fetch the raw source, the same way
 * the Blog and Guides sections do. The docs heading is demoted to \`##\` because
 * the summary block owns the single \`#\` heading.
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
      if (!match) return line;
      const rawPath = match[1];
      const normalizedPath = rawPath.endsWith('/') ? rawPath.slice(0, -1) : rawPath;
      const markdown = markdownByUrl.get(normalizedPath) ?? markdownByUrl.get(rawPath);
      const canonicalTarget = `${BASE_URL}${normalizedPath}/`;
      const withAbsolute = line.replace(`](${rawPath})`, `](${canonicalTarget})`);
      return markdown ? `${withAbsolute} ([markdown](${markdown}))` : withAbsolute;
    })
    .join('\n')
    .replace(/^# /, '## ');
}

export function GET() {
  // Blog and guides are separate MDX collections, so they are not part of the
  // docs page tree that llms(source).index() walks. Add them explicitly.
  const blog = getBlogEntries().map((post) => ({
    slug: post.slug,
    title: post.title,
    description: post.description,
  }));
  const guides = getGuideEntries().map((guide) => ({
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
