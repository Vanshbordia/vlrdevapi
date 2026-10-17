import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { metaSchema, pageSchema } from 'fumadocs-core/source/schema';
import { transformerTwoslash } from 'fumadocs-twoslash';
import { rehypeCodeDefaultOptions } from 'fumadocs-core/mdx-plugins';
import { remarkSteps } from 'fumadocs-core/mdx-plugins';
import { z } from 'zod';
import lastModified from 'fumadocs-mdx/plugins/last-modified';

// You can customize Zod schemas for frontmatter and `meta.json` here
// see https://fumadocs.dev/docs/mdx/collections
export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    schema: pageSchema,
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
  meta: {
    schema: metaSchema,
  },
});

const contentPageSchema = pageSchema.extend({
  date: z.string(),
  author: z.string().default('VLRdevAPI'),
});

export const blog = defineDocs({
  dir: 'content/blog',
  docs: {
    schema: contentPageSchema,
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
});

export const guides = defineDocs({
  dir: 'content/guides',
  docs: {
    schema: contentPageSchema,
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
});

/**
 * scripts/check_mdx_examples.py understands two markers inside code blocks:
 *
 *   `# doc-check: skip`         block is not executed by the checker.
 *   `# doc-check: allow-empty`  block runs, but empty output is acceptable
 *                               (e.g. a filtered loop over live data).
 *
 * Both markers exist only for the checker, so remove them from code blocks
 * before they render. The raw MDX files keep them, which means the checker
 * still sees them.
 */
const DOC_CHECK_MARKERS = ['# doc-check: skip', '# doc-check: allow-empty'];

interface MdastNode {
  type: string;
  value?: string;
  children?: MdastNode[];
}

function stripDocCheckMarker() {
  const hasMarker = (value: string) =>
    DOC_CHECK_MARKERS.some((marker) => value.includes(marker));

  const strip = (node: MdastNode) => {
    if (
      node.type === 'code' &&
      typeof node.value === 'string' &&
      hasMarker(node.value)
    ) {
      node.value = node.value
        .split('\n')
        .filter(
          (line) =>
            !DOC_CHECK_MARKERS.some((marker) => line.trim().startsWith(marker)),
        )
        .join('\n')
        .replace(/^\n+/, '');
    }
    node.children?.forEach(strip);
  };

  return (tree: unknown) => strip(tree as MdastNode);
}

export default defineConfig({
    plugins: [lastModified()],
  mdxOptions: {
    remarkPlugins: [remarkSteps, stripDocCheckMarker], 
    // MDX options
    rehypeCodeOptions: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
      transformers: [...(rehypeCodeDefaultOptions.transformers ?? []), transformerTwoslash()],
      // important: Shiki doesn't support lazy loading languages for codeblocks in Twoslash popups
      // make sure to define them first (e.g. the common ones)
      langs: ['py'],
    },
  
  },
});
