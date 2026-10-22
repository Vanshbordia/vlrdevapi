import type { Metadata } from 'next';
import { canonicalUrl } from '@/lib/shared';
import { Faq } from '@/components/landing/faq';
import { ModuleShowcase } from '@/components/landing/module-showcase';
import { Hero } from '@/components/landing/home/hero';
import { Features } from '@/components/landing/home/features';
import { Integrations } from '@/components/landing/home/integrations';
import { LatestPosts } from '@/components/landing/home/latest-posts';
import { FinalCta } from '@/components/landing/home/final-cta';

export const metadata: Metadata = {
  alternates: { canonical: canonicalUrl('/') },
};

export default function LandingPage() {
  return (
    <>
      <main id="main" tabIndex={-1} className="flex-1 bg-fd-canvas text-white">
        <Hero />
        <Features />

        {/* Namespace showcase */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
            <ModuleShowcase />
          </div>
        </section>

        <Integrations />
        <LatestPosts />

        {/* FAQ */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
            <Faq />
          </div>
        </section>

        <FinalCta />
      </main>
    </>
  );
}
