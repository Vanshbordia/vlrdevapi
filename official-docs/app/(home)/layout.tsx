import { SiteFooter } from '@/components/landing/site-footer';
import { SiteHeader } from '@/components/landing/site-header';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="dark flex min-h-dvh flex-col bg-black text-white selection:bg-[#ff4655]/30 selection:text-white">
      <SiteHeader />
      {children}
      <SiteFooter />
    </div>
  );
}
