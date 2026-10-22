import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { getGuideEntries } from '@/lib/source';

/**
 * Scoped 404 for an unknown guide slug.
 *
 * `app/not-found.tsx` handles unknown routes site-wide; this one gives a
 * visitor who landed on a dead guide link a route back into the library.
 */
export default function GuideNotFound() {
  const latest = getGuideEntries().slice(0, 3);

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <section className="relative overflow-hidden border-b border-white/10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_55%_55%_at_82%_-10%,rgba(255,70,85,0.14),transparent_70%)]"
        />

        <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-14 sm:px-8 sm:pb-20 sm:pt-20">
          <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-primary">
            HTTP 404 · Guides
          </p>
          <h1 className="mt-5 max-w-3xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.4rem]">
            That guide
            <br />
            <span className="text-fd-primary">isn&apos;t here.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-white/50 sm:text-base">
            The link may be from an older version of the site, or the guide may have been renamed.
            Every guide we publish is listed in the guides index.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/guides/"
              className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
            >
              All guides
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

      {latest.length > 0 ? (
        <section>
          <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
            <div className="flex items-center gap-4">
              <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                Latest guides
              </h2>
              <span aria-hidden="true" className="h-px flex-1 bg-white/10" />
            </div>

            <ul className="mt-6 grid gap-3 sm:grid-cols-3">
              {latest.map((guide) => (
                <li key={guide.slug}>
                  <Link
                    href={guide.url}
                    className="group relative flex h-full flex-col overflow-hidden border border-white/10 bg-fd-panel p-5 transition-colors hover:border-fd-primary/40"
                  >
                    <span
                      aria-hidden="true"
                      className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
                    />
                    <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                      {guide.date}
                    </span>
                    <span className="mt-4 text-lg font-medium leading-snug tracking-tight text-white/85 transition-colors group-hover:text-white">
                      {guide.title}
                    </span>
                    <span className="mt-auto inline-flex items-center gap-1.5 pt-6 text-[12px] font-medium text-fd-muted transition-colors group-hover:text-fd-primary">
                      Read guide
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
      ) : null}
    </main>
  );
}
