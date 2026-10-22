'use client';
import type { ReactNode } from 'react';
import { SearchProvider } from 'fumadocs-ui/contexts/search';
import SearchDialog from '@/components/search';

/**
 * Search providers for the documentation routes only.
 *
 * Mounting `SearchProvider` here rather than in the root layout keeps the
 * Orama index and the zbsearch client (~165 KB uncompressed) out of every
 * marketing page's bundle.
 */
export function DocsProvider({ children }: { children: ReactNode }) {
  return (
    <SearchProvider SearchDialog={SearchDialog} preload={false}>
      {children}
    </SearchProvider>
  );
}
