import type { ReactNode } from 'react';
import { MarketingShell } from '@/components/marketing/marketing-shell';

export default function LandingLayout({ children }: { children: ReactNode }) {
  return <MarketingShell>{children}</MarketingShell>;
}
