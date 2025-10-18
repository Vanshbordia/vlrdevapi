import { defineConfig, defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content',
   docs: {
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
});

export default defineConfig({
  lastModifiedTime: 'git',
});
