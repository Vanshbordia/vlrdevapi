import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { MarketingShell } from '@/components/marketing/marketing-shell';

/**
 * The 404 page needs its own title. Without it the page inherits the
 * homepage title and 404 traffic becomes indistinguishable from the homepage
 * in analytics.
 *
 * Next already emits `<meta name="robots" content="noindex">` for the
 * not-found route. `robots` is restated here so the inherited
 * `index, follow` from the root layout does not produce a second, conflicting
 * tag - both tags then agree that the page is not indexable.
 *
 * `openGraph` is replaced rather than merged by Next, so `siteName`, `type`
 * and `locale` are restated here.
 */
export const metadata: Metadata = {
  title: '404 - Page not found',
  robots: { index: false, follow: false },
  openGraph: {
    type: 'website',
    siteName: 'VLRdevAPI',
    locale: 'en_US',
    title: '404 - Page not found | VLRdevAPI',
    description: 'That page does not exist. Find the documentation, guides, and blog instead.',
  },
  twitter: {
    card: 'summary_large_image',
    title: '404 - Page not found | VLRdevAPI',
    description: 'That page does not exist. Find the documentation, guides, and blog instead.',
  },
};

const popularLinks = [
  {
    title: 'Getting Started',
    desc: 'Install vlrdevapi with pip and make your first query in seconds.',
    href: '/docs/getting-started',
    tag: 'Guide',
  },
  {
    title: 'API Reference',
    desc: 'Complete documentation for Matches, Players, Teams, Events, and Series.',
    href: '/docs/reference',
    tag: 'Docs',
  },
  {
    title: 'VLR.gg API for Python',
    desc: 'Why an unofficial Python SDK exists for VLR.gg and what data it returns.',
    href: '/vlr-gg-api',
    tag: 'Overview',
  },
  {
    title: 'Guides & Tutorials',
    desc: 'Learn how to build Discord bots, real-time monitors, and Pandas analytics.',
    href: '/guides',
    tag: 'Tutorials',
  },
  {
    title: 'Installation Guide',
    desc: 'System requirements, Python 3.11+ setup, and troubleshooting.',
    href: '/docs/installation',
    tag: 'Docs',
  },
  {
    title: 'FAQ',
    desc: 'Frequently asked questions about rate limits, data freshness, and VLR.gg.',
    href: '/faq',
    tag: 'Help',
  },
];

/**
 * The 404 page.
 *
 * This is a Server Component on purpose. Legacy URLs are redirected at the
 * edge with a real 301 (see `public/_redirects`), so nothing needs to run in
 * the browser to resolve them — an earlier version of this page kept a
 * client-side redirect table, which produced a hydration mismatch and was
 * invisible to crawlers that do not execute JavaScript.
 *
 * Cloudflare Pages serves the generated `404.html` with a 404 status.
 */
export default function NotFound() {
  return (
    <MarketingShell>
      <main id="main" tabIndex={-1} className="flex-1">
        <section className="relative overflow-hidden border-b border-white/10">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_55%_55%_at_82%_-10%,rgba(255,70,85,0.14),transparent_70%)]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 opacity-50 [background-image:linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_85%_65%_at_50%_0%,black,transparent_78%)]"
          />

          <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-14 sm:px-8 sm:pb-20 sm:pt-20">
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-primary">
              HTTP 404 · Page not found
            </p>
            <h1 className="mt-5 max-w-3xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.8rem]">
              We couldn&apos;t find
              <br />
              <span className="text-fd-primary">that page.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-white/50 sm:text-base">
              The link you followed may be outdated, moved, or mistyped. Use the links below to
              find what you need in the VLRdevAPI Python SDK docs.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
              >
                Back to home
                <ArrowUpRight
                  className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <Link
                href="/docs/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white/15 px-6 text-sm font-medium text-white/70 transition-colors hover:border-white/30 hover:text-white"
              >
                Browse the docs
                <ArrowUpRight
                  className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </div>
          </div>
        </section>

        <section>
          <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
            <div className="flex items-center gap-4">
              <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                Popular destinations
              </h2>
              <span aria-hidden="true" className="h-px flex-1 bg-white/10" />
            </div>

            <ul className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {popularLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="group relative flex h-full flex-col overflow-hidden border border-white/10 bg-fd-panel p-5 transition-colors hover:border-fd-primary/40"
                  >
                    <span
                      aria-hidden="true"
                      className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
                    />
                    <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                      {item.tag}
                    </span>
                    <span className="mt-4 text-lg font-medium tracking-tight text-white/85 transition-colors group-hover:text-white">
                      {item.title}
                    </span>
                    <span className="mt-2 text-[13.5px] leading-relaxed text-fd-subtle">
                      {item.desc}
                    </span>
                    <span className="mt-auto inline-flex items-center gap-1.5 pt-6 text-[12px] font-medium text-fd-muted transition-colors group-hover:text-fd-primary">
                      Read more
                      <ArrowUpRight
                        className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                        aria-hidden="true"
                      />
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </MarketingShell>
  );
}
