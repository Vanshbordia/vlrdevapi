'use client';
import type { ReactNode } from 'react';
import { SearchProvider } from 'fumadocs-ui/contexts/search';
import SearchDialog from '@/components/search';
import { I18nProvider } from 'fumadocs-ui/contexts/i18n';
import { i18n } from '@/lib/i18n';

/**
 * Search and i18n providers for the documentation routes only.
 *
 * Mounting `SearchProvider` here rather than in the root layout keeps the
 * Orama index and the zbsearch client (~165 KB uncompressed) out of every
 * marketing page's bundle.
 */
export function DocsProvider({
  children,
  locale = 'en',
}: {
  children: ReactNode;
  locale?: string;
}) {
  return (
    <I18nProvider {...i18n.provider(locale)}>
      <SearchProvider SearchDialog={SearchDialog} preload={false}>
        {children}
      </SearchProvider>
    </I18nProvider>
  );
}
