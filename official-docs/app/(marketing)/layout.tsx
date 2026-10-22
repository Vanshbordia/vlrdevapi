import type { ReactNode } from 'react';
import { MarketingShell } from '@/components/marketing/marketing-shell';

/**
 * Shared chrome for every marketing route (landing page, blog, guides, FAQ,
 * changelog and the "why" pages). Keeping this in one place prevents the
 * routes from drifting apart.
 */
export default function MarketingLayout({ children }: { children: ReactNode }) {
  return <MarketingShell>{children}</MarketingShell>;
}
