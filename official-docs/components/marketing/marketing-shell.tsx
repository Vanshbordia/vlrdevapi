import type { ReactNode } from 'react';
import { SiteFooter } from '@/components/landing/site-footer';
import { SiteHeader } from '@/components/landing/site-header';

/**
 * Shared chrome for every marketing route. Keeping this in one place prevents
 * the home and landing route groups from drifting apart.
 */
export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div className="dark flex min-h-dvh flex-col bg-black text-white selection:bg-[#ff4655]/30 selection:text-white">
      <SiteHeader />
      {children}
      <SiteFooter />
    </div>
  );
}
