import { source } from '@/lib/source';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/lib/layout.shared';
import { DocsProvider } from '@/components/docs-provider';
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { i18n } from '@/lib/i18n';

export const metadata: Metadata = {
  title: {
    template: '%s | VLRdevAPI',
    default: 'VLRdevAPI - Python SDK for Valorant Esports Data',
  },
};

export default async function Layout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!i18n.languages.includes(lang as any)) {
    notFound();
  }

  return (
    <DocsProvider locale={lang}>
      <DocsLayout tree={source.getPageTree(lang)} {...baseOptions()}>
        {children}
      </DocsLayout>
    </DocsProvider>
  );
}
