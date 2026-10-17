import { docs, blog, guides } from 'collections/server';
import { loader } from 'fumadocs-core/source';
import { docsContentRoute, docsImageRoute, docsRoute } from './shared';
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

export function getPageImage(page: (typeof source)['$inferPage']) {
  const segments = [...page.slugs, 'image.png'];

  return {
    segments,
    url: `${docsImageRoute}/${segments.join('/')}`,
  };
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
