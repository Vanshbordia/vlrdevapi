import { MarketingShell } from '@/components/marketing/marketing-shell';

export default function Layout({ children }: { children: React.ReactNode }) {
  return <MarketingShell>{children}</MarketingShell>;
}
