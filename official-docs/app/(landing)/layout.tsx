import type { ReactNode } from 'react';
import { SiteFooter } from '@/components/landing/site-footer';
import { SiteHeader } from '@/components/landing/site-header';

export default function LandingLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col bg-black text-white">
      <SiteHeader />
      {children}
      <SiteFooter />
    </div>
  );
}
