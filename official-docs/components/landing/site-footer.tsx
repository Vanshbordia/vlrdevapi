import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { Brand, BrandMark } from './brand';
import { GithubIcon } from './github-icon';

const columns = [
  {
    title: 'Documentation',
    links: [
      { label: 'Introduction', href: '/docs' },
      { label: 'Getting started', href: '/docs/getting-started' },
      { label: 'Quickstart', href: '/docs/quickstart' },
      { label: 'API reference', href: '/docs/reference' },
    ],
  },
  {
    title: 'Explore',
    links: [
      { label: 'Guides', href: '/guides' },
      { label: 'Blog', href: '/blog' },
      { label: 'Changelog', href: '/changelog' },
      { label: 'FAQ', href: '/faq' },
    ],
  },
  {
    title: 'Project',
    links: [
      { label: 'GitHub', href: 'https://github.com/vanshbordia/vlrdevapi', external: true },
      { label: 'PyPI', href: 'https://pypi.org/project/vlrdevapi/', external: true },
      { label: 'Read the Docs', href: 'https://vlrdevapi.readthedocs.io/', external: true },
      { label: 'MIT License', href: 'https://opensource.org/license/mit', external: true },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-fd-canvas">
      <div className="mx-auto w-full max-w-7xl px-5 sm:px-8">
        <div className="grid gap-12 py-14 sm:grid-cols-2 lg:grid-cols-[1.6fr_repeat(3,1fr)] lg:gap-8 lg:py-16">
          <div className="max-w-sm">
            <Brand />
            <p className="mt-4 text-[13.5px] leading-relaxed text-fd-muted">
              A type-safe Python client for Valorant esports data on VLR.gg. Built for the people
              who watch, analyze, and ship around the game.
            </p>
            <div className="mt-5 flex items-center gap-2">
              <Link
                href="https://github.com/vanshbordia/vlrdevapi"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                className="inline-flex size-8 items-center justify-center border border-white/10 text-fd-subtle transition-colors hover:border-white/25 hover:text-white"
              >
                <GithubIcon className="size-3.5" />
              </Link>
              <Link
                href="https://pypi.org/project/vlrdevapi/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-8 items-center border border-white/10 px-3 font-mono text-[12px] text-fd-subtle transition-colors hover:border-white/25 hover:text-white"
              >
                pypi.org/project/vlrdevapi
              </Link>
            </div>
          </div>

          {columns.map((column) => (
            <div key={column.title}>
              <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                {column.title}
              </h2>
              <ul className="mt-4 flex flex-col gap-2.5">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      {...('external' in link
                        ? { target: '_blank', rel: 'noopener noreferrer' }
                        : {})}
                      className="group inline-flex items-center gap-1 text-[13px] text-white/50 transition-colors hover:text-white"
                    >
                      {link.label}
                      {'external' in link ? (
                        <ArrowUpRight
                          className="size-3 text-white/20 transition-colors group-hover:text-white/50"
                          aria-hidden="true"
                        />
                      ) : null}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-3 border-t border-white/10 py-6 text-[12px] text-fd-muted sm:flex-row sm:items-center sm:justify-between">
          <p>
            &copy; {new Date().getFullYear()} VLRdevAPI. Not affiliated with Riot Games or VLR.gg.
          </p>
          <p className="inline-flex items-center gap-2">
            <span className="text-white">
              <BrandMark className="size-3" />
            </span>
            Open source · MIT · Python 3.11+
          </p>
        </div>

        <div aria-hidden="true" className="relative w-full overflow-hidden pb-2">
          <p className="w-full select-none whitespace-nowrap bg-gradient-to-b from-white/[0.08] via-white/[0.035] to-transparent bg-clip-text text-center text-[clamp(3.25rem,18vw,16rem)] font-medium leading-[1.3] tracking-[-0.06em] text-transparent">
            VLRdevAPI
          </p>
        </div>
      </div>
    </footer>
  );
}
