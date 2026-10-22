import { source } from '@/lib/source';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/lib/layout.shared';
import { DocsProvider } from '@/components/docs-provider';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    // Same separator as the root template, so every page on the site has a
    // consistent title format.
    template: '%s | VLRdevAPI',
    default: 'VLRdevAPI - Python SDK for Valorant Esports Data',
  },
};

export default function Layout({ children }: LayoutProps<'/docs'>) {
  return (
    <DocsProvider>
      <DocsLayout tree={source.getPageTree()} {...baseOptions()}>
        {children}
      </DocsLayout>
    </DocsProvider>
  );
}
