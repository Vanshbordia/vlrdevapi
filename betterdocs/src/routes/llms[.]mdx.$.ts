import { createFileRoute, notFound } from '@tanstack/react-router';
import { source } from '@/lib/source';
import { getLLMText } from '@/lib/get-llm-text';

export const Route = createFileRoute('/llms.mdx/$')({
  server: {
    handlers: {
      GET: async ({ params }) => {
        const slugs = params._splat?.split('/') ?? [];
        // Remove trailing .mdx from the last segment if present
        if (slugs.length > 0) {
          const last = slugs[slugs.length - 1];
          if (last.endsWith('.mdx')) {
            slugs[slugs.length - 1] = last.slice(0, -4);
          }
        }
        const page = source.getPage(slugs);
        if (!page) throw notFound();

        return new Response(await getLLMText(page), {
          headers: {
            'Content-Type': 'text/markdown',
          },
        });
      },
    },
  },
});