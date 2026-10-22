'use client';
import type { ReactNode } from 'react';
import { RootProvider } from 'fumadocs-ui/provider/next';

/**
 * Root providers for the whole app.
 *
 * The search engine (Orama + zbsearch, ~165 KB of client JS) is deliberately
 * **not** mounted here: it is scoped to the documentation routes by
 * `components/docs-provider.tsx`, so the landing page, blog, guides, FAQ,
 * changelog and the "why" pages never download it.
 *
 * The theme provider stays at the root so `next-themes` can keep `<html>`
 * in sync on every route.
 */
export function Provider({ children }: { children: ReactNode }) {
  return <RootProvider search={{ enabled: false }}>{children}</RootProvider>;
}
