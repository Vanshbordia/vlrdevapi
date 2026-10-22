import { docs, blog, guides } from 'collections/server';
import { loader } from 'fumadocs-core/source';
import { docsContentRoute, docsRoute } from './shared';
import { icons } from 'lucide-react';
import { createElement } from 'react';

// See https://fumadocs.dev/docs/headless/source-api for more info
export const source = loader({
  icon(icon) {
    if (!icon) {
      // You may set a default icon
      return;
    }
    if (icon in icons) return createElement(icons[icon as keyof typeof icons]);
  },
  baseUrl: docsRoute,
  source: docs.toFumadocsSource(),
  plugins: [],
});

export const blogSource = loader({
  baseUrl: '/blog',
  source: blog.toFumadocsSource(),
});

export const guidesSource = loader({
  baseUrl: '/guides',
  source: guides.toFumadocsSource(),
});

/**
 * Normalised view of a blog post or guide, built from the fumadocs source
 * rather than a second frontmatter parser.
 */
export interface ContentEntry {
  /** Route slug, e.g. `getting-started-with-vlrdevapi`. */
  slug: string;
  /** Absolute site path, e.g. `/guides/getting-started-with-vlrdevapi`. */
  url: string;
  title: string;
  description: string;
  /** ISO date string (`YYYY-MM-DD`) from the frontmatter. */
  date: string;
  author: string;
  /** Last modification time reported by the `lastModified()` plugin. */
  lastModified?: Date;
}

function toContentEntry(page: {
  slugs: string[];
  url: string;
  data: {
    title: string;
    description?: string;
    date: string;
    author: string;
    lastModified?: Date;
  };
}): ContentEntry {
  return {
    slug: page.slugs[0] ?? page.url.replace(/^\//, ''),
    url: page.url,
    title: page.data.title,
    description: page.data.description ?? '',
    date: page.data.date,
    author: page.data.author,
    lastModified: page.data.lastModified,
  };
}

/** Blog posts, newest first. */
export function getBlogEntries(): ContentEntry[] {
  return blogSource
    .getPages()
    .map(toContentEntry)
    .sort((a, b) => b.date.localeCompare(a.date));
}

/** Guides, newest first. */
export function getGuideEntries(): ContentEntry[] {
  return guidesSource
    .getPages()
    .map(toContentEntry)
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function getPageMarkdownUrl(page: (typeof source)['$inferPage']) {
  const segments = [...page.slugs, 'content.md'];

  return {
    segments,
    url: `${docsContentRoute}/${segments.join('/')}`,
  };
}

/**
 * `# doc-check: skip` and `# doc-check: allow-empty` exist only for
 * scripts/check_mdx_examples.py. The remark plugin in source.config.ts strips
 * them from rendered HTML, but the markdown served to LLMs (content.md,
 * llms-full.txt) comes from the processed source, so strip them here too.
 */
const DOC_CHECK_MARKERS = ['# doc-check: skip', '# doc-check: allow-empty'];

export function stripDocCheckMarkers(text: string) {
  return text
    .split('\n')
    .filter(
      (line) => !DOC_CHECK_MARKERS.some((marker) => line.trim().startsWith(marker)),
    )
    .join('\n');
}

export async function getLLMTextFor(page: {
  url: string;
  data: { title: string; getText: (type: 'processed') => Promise<string> };
}) {
  const processed = await page.data.getText('processed');

  return `# ${page.data.title} (${page.url})

${stripDocCheckMarkers(processed)}`;
}

export async function getLLMText(page: (typeof source)['$inferPage']) {
  return getLLMTextFor(page);
}
