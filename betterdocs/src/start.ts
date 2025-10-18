import { createMiddleware, createStart } from '@tanstack/react-start';
import { rewritePath } from 'fumadocs-core/negotiation';

const { rewrite: rewriteLLM } = rewritePath(
  '/docs/*path.mdx',
  '/llms.mdx/*path',
);

const llmMiddleware = createMiddleware().server(({ next, request }) => {
  const url = new URL(request.url);
  const path = rewriteLLM(url.pathname);

  if (path) {
    // For .mdx requests, redirect to the LLM route using a standard HTTP redirect
    const target = new URL(path, url);
    return Response.redirect(target, 307);
  }

  return next();
});

export const startInstance = createStart(() => {
  return {
    requestMiddleware: [llmMiddleware],
  };
});