'use client';

/**
 * Global error boundary.
 *
 * Catches failures in the root layout itself, so it has to render its own
 * `<html>`/`<body>` and cannot rely on anything from the app shell.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen items-center justify-center bg-fd-canvas px-6 text-white">
        <main id="main" className="max-w-xl text-center">
          <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-primary">
            HTTP 500
          </p>
          <h1 className="mt-4 text-3xl font-medium tracking-[-0.035em] sm:text-4xl">
            The site failed to load.
          </h1>
          <p className="mt-4 text-[15px] leading-relaxed text-white/50">
            An unexpected error interrupted the render. Try again, or head back to the docs.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              onClick={() => reset()}
              className="inline-flex h-11 items-center border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
            >
              Try again
            </button>
            {/*
              `global-error` replaces the root layout, so the Next.js router
              context may not exist here. A plain anchor is the only reliable
              way back to a working page.
            */}
            {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
            <a
              href="/docs/"
              className="inline-flex h-11 items-center border border-white/15 px-6 text-sm font-medium text-white/70 transition-colors hover:border-white/30 hover:text-white"
            >
              Browse the docs
            </a>
          </div>
        </main>
      </body>
    </html>
  );
}
