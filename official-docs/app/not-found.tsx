'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Logo } from '@/components/logo';

const REDIRECT_MAP: Record<string, string> = {
  // Teams
  '/docs/api/teams/completed-matches': '/docs/reference/team/completed-matches/',
  '/docs/api/teams/upcoming-matches': '/docs/reference/team/upcoming-matches/',
  '/docs/api/teams/info': '/docs/reference/team/info/',
  '/docs/api/teams/roster': '/docs/reference/team/roster/',
  '/docs/api/teams/previous-players': '/docs/reference/team/roster/',
  '/docs/api/teams/placements': '/docs/reference/team/placements/',
  '/docs/api/teams/transactions': '/docs/reference/team/transactions/',
  '/docs/api/teams/stats': '/docs/reference/team/stats/',
  '/docs/api/teams': '/docs/reference/team/',

  // Players
  '/docs/api/players/agent-stats': '/docs/reference/player/agents/',
  '/docs/api/players/matches': '/docs/reference/player/matches/',
  '/docs/api/players/profile': '/docs/reference/player/profile/',
  '/docs/api/players/info': '/docs/reference/player/info/',
  '/docs/api/players': '/docs/reference/player/',

  // Events
  '/docs/api/events/standings': '/docs/reference/events/standings/',
  '/docs/api/events/matches': '/docs/reference/events/matches/',
  '/docs/api/events/info': '/docs/reference/events/info/',
  '/docs/api/events/stages': '/docs/reference/events/stages/',
  '/docs/api/events/teams': '/docs/reference/events/teams/',
  '/docs/api/events/list-events': '/docs/reference/events/list/',
  '/docs/api/events/list': '/docs/reference/events/list/',
  '/docs/api/events/match-summary': '/docs/reference/events/matches/',
  '/docs/api/events': '/docs/reference/events/',

  // Matches
  '/docs/api/matches/upcoming': '/docs/reference/matches/upcoming/',
  '/docs/api/matches/live': '/docs/reference/matches/live/',
  '/docs/api/matches/completed': '/docs/reference/matches/completed/',
  '/docs/api/matches': '/docs/reference/matches/',

  // Series
  '/docs/api/series/info': '/docs/reference/series/info/',
  '/docs/api/series/matches': '/docs/reference/series/',
  '/docs/api/series/rounds': '/docs/reference/series/rounds/',
  '/docs/api/series/economy': '/docs/reference/series/economy/',
  '/docs/api/series/performance': '/docs/reference/series/performance/',
  '/docs/api/series/vods': '/docs/reference/series/vods/',
  '/docs/api/series': '/docs/reference/series/',

  // News
  '/docs/api/news': '/docs/reference/news/',
  '/docs/api/news/list': '/docs/reference/news/list/',
  '/docs/api/news/article': '/docs/reference/news/article/',

  // Search & Config
  '/docs/api/search': '/docs/reference/',
  '/docs/api/status': '/docs/reference/',
  '/docs/config': '/docs/',
  '/docs/rate-limiting': '/docs/',
};

function resolveRedirect(rawPath: string): string | null {
  const clean = rawPath.replace(/\/+$/, '');
  if (REDIRECT_MAP[clean]) {
    return REDIRECT_MAP[clean];
  }
  if (clean.startsWith('/docs/api/search')) {
    return '/docs/reference/';
  }
  if (clean.startsWith('/docs/api/status')) {
    return '/docs/reference/';
  }
  if (clean.startsWith('/docs/api')) {
    return '/docs/reference/';
  }
  return null;
}

const popularLinks = [
  {
    title: 'Getting Started',
    desc: 'Install vlrdevapi with pip and make your first query in seconds.',
    href: '/docs/getting-started/',
    tag: 'Guide',
  },
  {
    title: 'API Reference',
    desc: 'Complete documentation for Matches, Players, Teams, Events, and Series.',
    href: '/docs/reference/',
    tag: 'Docs',
  },
  {
    title: 'VLR.gg API for Python',
    desc: 'Why an unofficial Python SDK exists for VLR.gg and what data it returns.',
    href: '/vlr-gg-api/',
    tag: 'Overview',
  },
  {
    title: 'Guides & Tutorials',
    desc: 'Learn how to build Discord bots, real-time monitors, and Pandas analytics.',
    href: '/guides/',
    tag: 'Tutorials',
  },
  {
    title: 'Installation Guide',
    desc: 'System requirements, Python 3.11+ setup, and troubleshooting.',
    href: '/docs/installation/',
    tag: 'Docs',
  },
  {
    title: 'FAQ',
    desc: 'Frequently asked questions about rate limits, data freshness, and VLR.gg.',
    href: '/faq/',
    tag: 'Help',
  },
];

export default function NotFound() {
  const pathname = usePathname();
  const [redirectTarget, setRedirectTarget] = useState<string | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);

  useEffect(() => {
    // Determine path from pathname or window.location for static servers
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : pathname || '';
    const target = resolveRedirect(currentPath);

    if (target) {
      setRedirectTarget(target);
      setIsRedirecting(true);
      // Client-side automatic redirect
      window.location.replace(target);
    }
  }, [pathname]);

  if (isRedirecting && redirectTarget) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background px-6 text-center text-foreground">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-2 border-fd-primary border-t-transparent mb-4" />
        <h1 className="text-xl font-bold">Redirecting...</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This page has moved to{' '}
          <Link href={redirectTarget} className="text-fd-primary underline">
            {redirectTarget}
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      {/* Top Navigation */}
      <header className="border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="inline-flex items-center gap-2 font-bold tracking-tight text-foreground hover:opacity-90">
            <Logo className="size-5" />
            <span>VLRdevAPI</span>
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/docs/" className="text-muted-foreground hover:text-foreground transition-colors">
              Documentation
            </Link>
            <Link href="/guides/" className="text-muted-foreground hover:text-foreground transition-colors">
              Guides
            </Link>
            <Link
              href="/"
              className="inline-flex h-8 items-center justify-center bg-foreground px-3.5 text-xs font-medium text-background transition-all hover:brightness-110"
            >
              Home
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 mx-auto w-full max-w-5xl px-6 py-16 md:py-24">
        <div className="flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 rounded border border-border bg-muted/30 px-3 py-1 font-mono text-xs uppercase tracking-wider text-muted-foreground mb-6">
            <span>HTTP 404</span>
            <span>&middot;</span>
            <span>Page Not Found</span>
          </div>

          <h1 className="font-heading text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl text-foreground">
            We couldn&apos;t find that page
          </h1>

          <p className="mt-4 max-w-xl text-base text-muted-foreground sm:text-lg">
            The link you followed may be outdated, moved, or mistyped. Use the links below to find what you need in the VLRdevAPI Python SDK docs.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/"
              className="inline-flex h-10 items-center justify-center bg-foreground px-5 text-sm font-medium tracking-tight text-background transition-all hover:brightness-110"
            >
              Back to Home
            </Link>
            <Link
              href="/docs/"
              className="inline-flex h-10 items-center justify-center border border-border bg-background px-5 text-sm font-medium tracking-tight text-foreground transition-all hover:bg-muted"
            >
              Browse Docs
            </Link>
          </div>
        </div>

        {/* Popular Destinations Grid */}
        <div className="mt-16 border-t border-border pt-12">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground text-center sm:text-left mb-6">
            Popular Documentation &amp; Resources
          </h2>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {popularLinks.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="group flex flex-col justify-between border border-border bg-background/50 p-5 transition-all hover:border-fd-primary/50 hover:bg-muted/20"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-foreground transition-colors group-hover:text-fd-primary">
                      {item.title}
                    </h3>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border border-border text-muted-foreground">
                      {item.tag}
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed text-muted-foreground">
                    {item.desc}
                  </p>
                </div>
                <div className="mt-4 flex items-center gap-1 text-xs text-fd-primary font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>Read more</span>
                  <span>&rarr;</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 text-center text-xs text-muted-foreground">
        <div className="mx-auto max-w-7xl px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>&copy; {new Date().getFullYear()} VLRdevAPI &middot; Open source Python SDK</p>
          <div className="flex items-center gap-4">
            <Link href="https://github.com/vanshbordia/vlrdevapi" target="_blank" rel="noopener noreferrer" className="hover:text-foreground">
              GitHub
            </Link>
            <Link href="https://pypi.org/project/vlrdevapi/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground">
              PyPI
            </Link>
            <Link href="/faq/" className="hover:text-foreground">
              FAQ
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
