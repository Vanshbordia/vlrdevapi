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
import { Brand } from './brand';
import { GithubIcon } from './github-icon';

const links = [
  { href: '/docs/', label: 'Docs' },
  { href: '/guides/', label: 'Guides' },
  { href: '/blog/', label: 'Blog' },
  { href: '/faq/', label: 'FAQ' },
  { href: '/changelog/', label: 'Changelog' },
];

const whyPages = [
  {
    href: '/valorant-api-python/',
    label: 'Valorant API for Python',
    description: 'Typed models, no API key, straight from PyPI.',
    icon: Code2,
  },
  {
    href: '/vlr-gg-api/',
    label: 'VLR.gg API',
    description: 'An unofficial data layer for VLR.gg pages.',
    icon: Database,
  },
  {
    href: '/valorant-esports-api/',
    label: 'Valorant esports API',
    description: 'VCT matches, events, stages, and standings.',
    icon: Trophy,
  },
  {
    href: '/valorant-stats-api/',
    label: 'Valorant stats API',
    description: 'Player, team, and match stats ready to analyze.',
    icon: BarChart3,
  },
];

const whyComparisons = [
  {
    href: '/blog/vlrdevapi-vs-other-valorant-apis/',
    label: 'Other APIs',
    description: 'See how the SDK compares.',
    icon: ArrowLeftRight,
  },
  {
    href: '/blog/vlrdevapi-vs-web-scraping/',
    label: 'Web scraping',
    description: 'Why typed data beats a parser.',
    icon: Globe,
  },
];

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const [whyOpen, setWhyOpen] = useState(false);
  const [whyMobileOpen, setWhyMobileOpen] = useState(false);
  const whyRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const normalizedPath = pathname.endsWith('/') ? pathname : `${pathname}/`;
  const whyActive = whyPages.some((link) => normalizedPath.startsWith(link.href));

  useEffect(() => {
    if (!open) return;
    const original = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = original;
    };
  }, [open]);

  useEffect(() => {
    if (!whyOpen) return;

    const onPointerDown = (event: PointerEvent) => {
      if (!whyRef.current?.contains(event.target as Node)) {
        setWhyOpen(false);
      }
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setWhyOpen(false);
    };

    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [whyOpen]);

  return (
    <>
      <a
        href="#main"
        className="fixed left-4 top-3 z-[70] -translate-y-20 bg-white px-4 py-2 text-sm font-medium text-black transition-transform focus:translate-y-0"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-50 border-b border-white/10 bg-black/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-6 px-5 sm:px-8">
          <div className="flex items-center gap-3">
            <Brand />
            <span className="hidden border border-white/15 px-2 py-0.5 font-mono text-[12px] tracking-wide text-white/40 sm:inline">
              v3.0
            </span>
          </div>

          <nav aria-label="Main navigation" className="hidden flex-1 items-center gap-1 lg:flex">
            {links.map((link) => {
              const active = normalizedPath.startsWith(link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  aria-current={active ? 'page' : undefined}
                  className={`group relative px-3.5 py-1.5 text-[13.5px] font-medium transition-colors hover:text-white ${
                    active ? 'text-white' : 'text-white/60'
                  }`}
                >
                  {link.label}
                  <span
                    aria-hidden="true"
                    className={`absolute inset-x-3.5 bottom-0.5 h-px origin-left bg-[#ff4655] transition-transform duration-200 group-hover:scale-x-100 ${
                      active ? 'scale-x-100' : 'scale-x-0'
                    }`}
                  />
                </Link>
              );
            })}

            <div
              ref={whyRef}
              className="relative"
              onMouseEnter={() => setWhyOpen(true)}
              onMouseLeave={() => setWhyOpen(false)}
              onBlur={(event) => {
                if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
                  setWhyOpen(false);
                }
              }}
            >
              <button
                type="button"
                aria-haspopup="true"
                aria-expanded={whyOpen}
                aria-controls="why-menu"
                onClick={() => setWhyOpen(true)}
                className={`group relative inline-flex items-center gap-1.5 px-3.5 py-1.5 text-[13.5px] font-medium transition-colors hover:text-white ${
                  whyActive ? 'text-white' : 'text-white/60'
                }`}
              >
                Why
                <ChevronDown
                  aria-hidden="true"
                  className={`size-3.5 transition-transform duration-200 ${
                    whyOpen ? 'rotate-180 text-[#ff8d97]' : ''
                  }`}
                />
                <span
                  aria-hidden="true"
                  className={`absolute inset-x-3.5 bottom-0.5 h-px origin-left bg-[#ff4655] transition-transform duration-200 group-hover:scale-x-100 ${
                    whyActive ? 'scale-x-100' : 'scale-x-0'
                  }`}
                />
              </button>

              {whyOpen ? (
                <div className="absolute right-0 top-full z-50 pt-4">
                  <div
                    id="why-menu"
                    className="w-[480px] max-w-[calc(100vw-2rem)] border border-white/10 bg-black shadow-2xl shadow-black/60"
                  >
                    <div className="grid grid-cols-2">
                      {whyPages.map((link, index) => {
                        const Icon = link.icon;

                        return (
                          <Link
                            key={link.href}
                            href={link.href}
                            onClick={() => setWhyOpen(false)}
                            className={`group relative flex h-full flex-col gap-2.5 p-4 transition-colors hover:bg-white/[0.03] ${
                              index % 2 === 1 ? 'border-l border-white/10' : ''
                            } ${index >= 2 ? 'border-t border-white/10' : ''}`}
                          >
                            <span className="flex size-8 items-center justify-center border border-white/10 text-white/55 transition-colors group-hover:border-[#ff4655]/40 group-hover:text-[#ff8d97]">
                              <Icon className="size-4" aria-hidden="true" />
                            </span>
                            <span className="flex flex-col gap-0.5">
                              <span className="text-[13px] font-medium text-white/85 transition-colors group-hover:text-white">
                                {link.label}
                              </span>
                              <span className="text-[12px] leading-relaxed text-white/45">
                                {link.description}
                              </span>
                            </span>
                          </Link>
                        );
                      })}
                    </div>

                    <div className="border-t border-white/10 p-2">
                      <p className="px-2 pb-1 pt-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                        Compare
                      </p>
                      <div className="grid grid-cols-2 gap-1">
                        {whyComparisons.map((link) => {
                          const Icon = link.icon;

                          return (
                            <Link
                              key={link.href}
                              href={link.href}
                              onClick={() => setWhyOpen(false)}
                              className="group flex items-center gap-2 p-2.5 text-[12.5px] text-white/55 transition-colors hover:bg-white/[0.03] hover:text-white"
                            >
                              <Icon
                                className="size-3.5 shrink-0 text-white/30 transition-colors group-hover:text-[#ff8d97]"
                                aria-hidden="true"
                              />
                              <span className="min-w-0">
                                <span className="block">{link.label}</span>
                                <span className="mt-0.5 block text-[12px] leading-snug text-white/30">
                                  {link.description}
                                </span>
                              </span>
                            </Link>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </nav>

          <div className="ml-auto hidden items-center gap-2.5 lg:flex">
            <Link
              href="https://github.com/vanshbordia/vlrdevapi"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="VLRdevAPI on GitHub"
              className="inline-flex size-9 items-center justify-center border border-white/10 text-white/60 transition-colors hover:border-white/25 hover:text-white"
            >
              <GithubIcon className="size-4" />
            </Link>
            <Link
              href="https://pypi.org/project/vlrdevapi/"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 text-[13.5px] font-medium text-white/60 transition-colors hover:text-white"
            >
              PyPI
            </Link>
            <Link
              href="/docs/"
              className="group inline-flex h-9 items-center gap-1.5 border border-white bg-white px-4 text-[13.5px] font-medium text-black transition-colors hover:bg-[#ff4655] hover:text-white"
            >
              Read the docs
              <ArrowUpRight
                className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>

          <button
            type="button"
            onClick={() => {
              setOpen((value) => !value);
              setWhyOpen(false);
              setWhyMobileOpen(false);
            }}
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            className="ml-auto inline-flex size-9 items-center justify-center border border-white/10 text-white/70 transition-colors hover:border-white/25 hover:text-white lg:hidden"
          >
            {open ? <X className="size-4" /> : <Menu className="size-4" />}
          </button>
        </div>
      </header>

      {open ? (
        <div className="fixed inset-0 top-16 z-40 overflow-y-auto bg-black lg:hidden">
          <nav aria-label="Mobile navigation" className="flex flex-col px-5 py-4 sm:px-8">
            {links.map((link) => {
              const active = normalizedPath.startsWith(link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => {
                    setOpen(false);
                    setWhyMobileOpen(false);
                  }}
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
                onClick={() => setWhyMobileOpen((value) => !value)}
                aria-expanded={whyMobileOpen}
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
                    whyMobileOpen ? 'rotate-180 text-[#ff8d97]' : ''
                  }`}
                />
              </button>

              {whyMobileOpen ? (
                <div id="mobile-why-menu" className="pb-4">
                  <div className="grid gap-2">
                    {whyPages.map((link) => {
                      const active = normalizedPath.startsWith(link.href);
                      const Icon = link.icon;

                      return (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => {
                            setOpen(false);
                            setWhyMobileOpen(false);
                          }}
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
                                : 'border-white/10 text-white/50 group-hover:text-white/80'
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
                            <span className="mt-0.5 block text-[12px] leading-snug text-white/35">
                              {link.description}
                            </span>
                          </span>
                        </Link>
                      );
                    })}
                  </div>

                  <p className="mt-3 px-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                    Compare
                  </p>
                  <div className="mt-1 grid grid-cols-2 gap-1">
                    {whyComparisons.map((link) => {
                      const Icon = link.icon;

                      return (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => {
                            setOpen(false);
                            setWhyMobileOpen(false);
                          }}
                          className="flex items-center gap-2 border border-white/10 px-2.5 py-2.5 text-[12px] text-white/55 transition-colors hover:border-white/25 hover:text-white"
                        >
                          <Icon
                            className="size-3.5 shrink-0 text-white/30"
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
                onClick={() => setOpen(false)}
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
                  onClick={() => setOpen(false)}
                  className="inline-flex h-11 items-center justify-center gap-2 border border-white/15 px-5 text-sm font-medium text-white/80"
                >
                  <GithubIcon className="size-4" />
                  GitHub
                </Link>
                <Link
                  href="https://pypi.org/project/vlrdevapi/"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setOpen(false)}
                  className="inline-flex h-11 items-center justify-center border border-white/15 px-5 text-sm font-medium text-white/80"
                >
                  PyPI
                </Link>
              </div>
            </div>
            <p className="mt-8 pb-8 font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
              VLR.gg data · typed for Python
            </p>
          </nav>
        </div>
      ) : null}
    </>
  );
}
