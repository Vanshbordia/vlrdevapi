'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { ArrowUpRight } from 'lucide-react';

/**
 * Route-level error boundary.
 *
 * Next.js renders this when a Server Component throws during a client-side
 * navigation. Without it the router leaves the user on a blank page.
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Surfaces the failure in the browser console during development.
    console.error(error);
  }, [error]);

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <section className="relative overflow-hidden border-b border-white/10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_55%_55%_at_82%_-10%,rgba(255,70,85,0.14),transparent_70%)]"
        />

        <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-14 sm:px-8 sm:pb-20 sm:pt-20">
          <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-primary">
            Something went wrong
          </p>
          <h1 className="mt-5 max-w-3xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.4rem]">
            This page
            <br />
            <span className="text-fd-primary">failed to load.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-white/50 sm:text-base">
            The error has been logged. Try again, or head back to the docs.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => reset()}
              className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
            >
              Try again
              <ArrowUpRight
                className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </button>
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
    </main>
  );
}
