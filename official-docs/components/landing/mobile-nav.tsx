'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ArrowLeftRight,
  ArrowUpRight,
  BarChart3,
  ChevronDown,
  Code2,
  Database,
  Globe,
  Menu,
  Trophy,
  X,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { GithubIcon } from './github-icon';

const links = [
  { href: '/docs', label: 'Docs' },
  { href: '/guides', label: 'Guides' },
  { href: '/blog', label: 'Blog' },
  { href: '/faq', label: 'FAQ' },
  { href: '/changelog', label: 'Changelog' },
];

const whyPages = [
  {
    href: '/valorant-api-python',
    label: 'Valorant API for Python',
    description: 'Typed models, no API key, straight from PyPI.',
    icon: Code2,
  },
  {
    href: '/vlr-gg-api',
    label: 'VLR.gg API',
    description: 'An unofficial data layer for VLR.gg pages.',
    icon: Database,
  },
  {
    href: '/valorant-esports-api',
    label: 'Valorant esports API',
    description: 'VCT matches, events, stages, and standings.',
    icon: Trophy,
  },
  {
    href: '/valorant-stats-api',
    label: 'Valorant stats API',
    description: 'Player, team, and match stats ready to analyze.',
    icon: BarChart3,
  },
];

const whyComparisons = [
  {
    href: '/blog/vlrdevapi-vs-other-valorant-apis',
    label: 'Other APIs',
    description: 'See how the SDK compares.',
    icon: ArrowLeftRight,
  },
  {
    href: '/blog/vlrdevapi-vs-web-scraping',
    label: 'Web scraping',
    description: 'Why typed data beats a parser.',
    icon: Globe,
  },
];

/**
 * The mobile drawer.
 *
 * Behaves as a modal dialog: focus moves into the panel on open, Tab is
 * trapped inside it, Escape closes it, and focus returns to the toggle.
 */
export function MobileNav() {
  const [open, setOpen] = useState(false);
  const [whyOpen, setWhyOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);
  const pathname = usePathname();
  const normalizedPath = pathname.endsWith('/') ? pathname : `${pathname}/`;
  const whyActive = whyPages.some((link) => normalizedPath.startsWith(link.href));

  // Lock the page behind the drawer.
  useEffect(() => {
    if (!open) return;

    const original = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = original;
    };
  }, [open]);

  // Move focus in, trap Tab, close on Escape, restore focus on close.
  useEffect(() => {
    if (!open) return;

    const panel = panelRef.current;
    panel?.focus();

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
        toggleRef.current?.focus();
        return;
      }

      if (event.key !== 'Tab' || !panel) return;

      const focusable = panel.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );

      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);

    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open]);

  const close = () => {
    setOpen(false);
    setWhyOpen(false);
  };

  return (
    <>
      <button
        ref={toggleRef}
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? 'Close menu' : 'Open menu'}
        aria-expanded={open}
        aria-controls="mobile-menu"
        className="ml-auto inline-flex size-9 items-center justify-center border border-white/10 text-white/80 transition-colors hover:border-white/25 hover:text-white lg:hidden"
      >
        {open ? <X className="size-4" /> : <Menu className="size-4" />}
      </button>

      {open ? (
        <div className="fixed inset-0 top-16 z-40 overflow-y-auto bg-black lg:hidden">
          <div
            id="mobile-menu"
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-label="Site menu"
            tabIndex={-1}
            className="flex flex-col px-5 py-4 outline-none sm:px-8"
          >
            <nav aria-label="Mobile navigation" className="flex flex-col">
              {links.map((link) => {
                const active = normalizedPath.startsWith(link.href);

                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={close}
                    aria-current={active ? 'page' : undefined}
                    className={`flex items-center justify-between border-b border-white/10 py-4 text-2xl font-medium tracking-tight transition-colors hover:text-white ${
                      active ? 'text-white' : 'text-white/75'
                    }`}
                  >
                    {link.label}
                    {active ? <span aria-hidden="true" className="size-1.5 bg-[#ff4655]" /> : null}
                  </Link>
                );
              })}

              <div className="border-b border-white/10">
                <button
                  type="button"
                  onClick={() => setWhyOpen((value) => !value)}
                  aria-expanded={whyOpen}
                  aria-controls="mobile-why-menu"
                  className={`flex w-full items-center justify-between py-4 text-2xl font-medium tracking-tight transition-colors hover:text-white ${
                    whyActive ? 'text-white' : 'text-white/75'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    Why
                    {whyActive ? (
                      <span aria-hidden="true" className="size-1.5 bg-[#ff4655]" />
                    ) : null}
                  </span>
                  <ChevronDown
                    aria-hidden="true"
                    className={`size-5 transition-transform duration-200 ${
                      whyOpen ? 'rotate-180 text-[#ff8d97]' : ''
                    }`}
                  />
                </button>

                {whyOpen ? (
                  <div id="mobile-why-menu" className="pb-4">
                    <div className="grid gap-2">
                      {whyPages.map((link) => {
                        const active = normalizedPath.startsWith(link.href);
                        const Icon = link.icon;

                        return (
                          <Link
                            key={link.href}
                            href={link.href}
                            onClick={close}
                            aria-current={active ? 'page' : undefined}
                            className={`group flex items-start gap-3 border p-3 transition-colors ${
                              active
                                ? 'border-[#ff4655]/50 bg-[#ff4655]/[0.04]'
                                : 'border-white/10 hover:border-white/25'
                            }`}
                          >
                            <span
                              className={`flex size-8 shrink-0 items-center justify-center border transition-colors ${
                                active
                                  ? 'border-[#ff4655]/40 text-[#ff8d97]'
                                  : 'border-white/10 text-white/60 group-hover:text-white/80'
                              }`}
                            >
                              <Icon className="size-4" aria-hidden="true" />
                            </span>
                            <span className="min-w-0">
                              <span
                                className={`block text-[14px] font-medium ${
                                  active ? 'text-white' : 'text-white/75'
                                }`}
                              >
                                {link.label}
                              </span>
                              <span className="mt-0.5 block text-[12px] leading-snug text-fd-subtle">
                                {link.description}
                              </span>
                            </span>
                          </Link>
                        );
                      })}
                    </div>

                    <p className="mt-3 px-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                      Compare
                    </p>
                    <div className="mt-1 grid grid-cols-2 gap-1">
                      {whyComparisons.map((link) => {
                        const Icon = link.icon;

                        return (
                          <Link
                            key={link.href}
                            href={link.href}
                            onClick={close}
                            className="flex items-center gap-2 border border-white/10 px-2.5 py-2.5 text-[12px] text-white/65 transition-colors hover:border-white/25 hover:text-white"
                          >
                            <Icon
                              className="size-3.5 shrink-0 text-fd-muted"
                              aria-hidden="true"
                            />
                            {link.label}
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="mt-6 flex flex-col gap-2.5">
                <Link
                  href="/docs/"
                  onClick={close}
                  className="inline-flex h-11 items-center justify-center gap-1.5 border border-white bg-white px-5 text-sm font-medium text-black"
                >
                  Read the docs
                  <ArrowUpRight className="size-4" aria-hidden="true" />
                </Link>
                <div className="grid grid-cols-2 gap-2.5">
                  <Link
                    href="https://github.com/vanshbordia/vlrdevapi"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={close}
                    className="inline-flex h-11 items-center justify-center gap-2 border border-white/15 px-5 text-sm font-medium text-white/80"
                  >
                    <GithubIcon className="size-4" />
                    GitHub
                  </Link>
                  <Link
                    href="https://pypi.org/project/vlrdevapi/"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={close}
                    className="inline-flex h-11 items-center justify-center gap-2 border border-white/15 px-5 text-sm font-medium text-white/80"
                  >
                    <GithubIcon className="size-4" />
                    PyPI
                  </Link>
                </div>
              </div>
              <p className="mt-8 pb-8 font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                VLR.gg data · typed for Python
              </p>
            </nav>
          </div>
        </div>
      ) : null}
    </>
  );
}
