'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from '@/components/logo';

const navLinks = [
  { href: '/docs/', label: 'Docs' },
  { href: '/guides/', label: 'Guides' },
  { href: '/blog/', label: 'Blog' },
  { href: '/faq/', label: 'FAQ' },
];

const resourceLinks = [
  { href: '/docs/getting-started/', label: 'Getting Started', desc: 'Install and make your first API call' },
  { href: '/docs/', label: 'API Reference', desc: 'Complete endpoint documentation' },
  { href: '/changelog/', label: 'Changelog', desc: 'Release history and version notes' },
  { href: '/faq/', label: 'FAQ', desc: 'Frequently asked questions' },
];

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 z-50 flex items-center pt-2.5 w-full">
      <div className="relative mx-auto flex w-full max-w-7xl items-center gap-1 px-6">
        <div className="relative z-60 flex h-11 flex-1 items-center justify-between bg-foreground pl-6 pr-0">
          <Link href="/" className="inline-flex shrink-0 items-center gap-2 text-sm font-bold tracking-tight text-background">
            <Logo className="size-5" />
            VLRdevAPI
          </Link>
          <nav aria-label="Primary navigation" className="hidden h-full lg:flex">
            <div className="group relative flex items-center justify-center">
              <button
                type="button"
                className="relative inline-flex h-full items-center gap-0.5 px-5 py-0 text-sm leading-none font-medium tracking-tight text-background transition-colors"
              >
                Resources
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="size-3.5 opacity-70 transition-transform duration-200 group-hover:rotate-180" aria-hidden="true">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>
              <div className="absolute top-full left-0 mt-1.5 w-72 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <ul className="flex w-full flex-col bg-foreground shadow-lg">
                  {resourceLinks.map((link) => (
                    <li key={link.href}>
                      <Link
                        href={link.href}
                        className="flex flex-col gap-1 px-5 py-4 transition-colors hover:bg-white/10"
                      >
                        <span className="text-sm leading-none font-medium tracking-tight text-background">{link.label}</span>
                        <span className="text-xs leading-tight tracking-tight text-background/60">{link.desc}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="inline-flex items-center gap-0.5 px-5 text-sm leading-none font-medium tracking-tight transition-colors text-background"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
        <nav aria-label="Actions" className="hidden items-center gap-1 lg:flex">
          <Link
            href="https://pypi.org/project/vlrdevapi/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center h-11 font-medium tracking-tight transition-colors px-4 text-sm gap-1.5 border border-foreground/20 bg-background text-foreground hover:bg-muted"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M16 16v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4"/><path d="M8 8h4V4h4v4"/><rect x="2" y="14" width="8" height="6" rx="1"/><rect x="14" y="14" width="8" height="6" rx="1"/></svg>
            <span>PyPI</span>
          </Link>
          <Link
            href="https://github.com/vanshbordia/vlrdevapi"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center h-11 font-medium tracking-tight transition-colors px-4 text-sm gap-1.5 border border-foreground/20 bg-background text-foreground hover:bg-muted"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" clipRule="evenodd" d="M11.9317 1C5.91925 1 1 6.07047 1 12.2677C1 17.1973 4.14286 21.4227 8.51553 22.972C9.06211 23.1129 9.19876 22.6903 9.19876 22.4086C9.19876 22.1269 9.19876 21.4227 9.19876 20.4368C6.19255 21.141 5.50932 19.0283 5.50932 19.0283C4.96273 17.7607 4.2795 17.3382 4.2795 17.3382C3.32298 16.6339 4.41615 16.6339 4.41615 16.6339C5.50932 16.7748 6.0559 17.7607 6.0559 17.7607C7.01242 19.5917 8.65217 19.0283 9.19876 18.7466C9.3354 18.0424 9.6087 17.479 9.88199 17.1973C7.42236 16.9156 4.96273 15.9297 4.96273 11.5635C4.96273 10.2959 5.37267 9.30993 6.0559 8.6057C5.91925 8.32401 5.50932 7.19724 6.19255 5.64793C6.19255 5.64793 7.14907 5.36624 9.19876 6.7747C10.0186 6.49301 10.9752 6.35216 11.9317 6.35216C12.8882 6.35216 13.8447 6.49301 14.6646 6.7747C16.7143 5.36624 17.6708 5.64793 17.6708 5.64793C18.2174 7.19724 17.9441 8.32401 17.8075 8.6057C18.4907 9.45078 18.9006 10.4367 18.9006 11.5635C18.9006 15.9297 16.3043 16.7748 13.8447 17.0565C14.2547 17.6199 14.6646 18.3241 14.6646 19.31C14.6646 20.8593 14.6646 21.9861 14.6646 22.4086C14.6646 22.6903 14.8012 23.1129 15.4845 22.972C19.8571 21.4227 23 17.1973 23 12.2677C22.8634 6.07047 17.9441 1 11.9317 1Z" />
            </svg>
            <span>GitHub</span>
          </Link>
          <Link
            href="/docs/"
            className="inline-flex items-center justify-center h-11 gap-1 font-medium tracking-tight border border-foreground text-foreground hover:bg-muted px-5 text-sm transition-colors duration-300 bg-background"
          >
            Get Started
          </Link>
        </nav>
        {/* Mobile hamburger */}
        <button
          type="button"
          className="relative z-60 flex size-11 items-center justify-center lg:hidden text-foreground"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
        >
          <div className="relative size-5">
            <span className={`absolute left-0 block h-0.5 w-full bg-foreground transition-all duration-300 ${menuOpen ? 'top-1/2 -translate-y-1/2 rotate-45' : 'top-1'}`} />
            <span className={`absolute left-0 block h-0.5 w-full bg-foreground transition-all duration-300 ${menuOpen ? 'opacity-0' : 'opacity-100 top-1/2 -translate-y-1/2'}`} />
            <span className={`absolute left-0 block h-0.5 w-full bg-foreground transition-all duration-300 ${menuOpen ? 'bottom-1/2 translate-y-1/2 -rotate-45' : 'bottom-1'}`} />
          </div>
        </button>
        {/* Mobile overlay */}
        <div
          className={`fixed inset-0 z-40 bg-background/50 transition-opacity duration-300 lg:hidden ${menuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
          aria-hidden="true"
          onClick={() => setMenuOpen(false)}
        />
        {/* Mobile menu */}
        <div
          className={`absolute top-full right-6 left-6 z-50 max-h-[calc(100dvh-64px)] overflow-y-auto bg-foreground shadow-2xl transition-all duration-300 lg:hidden ${menuOpen ? 'visible translate-y-0 opacity-100' : 'invisible -translate-y-2 opacity-0'}`}
        >
          <div className="px-5 py-5">
            <nav className="flex flex-col">
              <div className="border-b border-white/10">
                <span className="flex w-full items-center py-3.5 text-base font-medium tracking-tight text-background">
                  Resources
                </span>
                <div className="pb-3">
                  <ul className="flex flex-col gap-1">
                    {resourceLinks.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          className="flex flex-col gap-1 py-2.5 transition-colors hover:bg-white/5"
                          onClick={() => setMenuOpen(false)}
                        >
                          <span className="text-sm leading-none font-medium tracking-tight text-background">{link.label}</span>
                          <span className="text-xs leading-tight tracking-tight text-background/60">{link.desc}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="border-b border-white/10 py-3.5 text-base font-medium tracking-tight text-background transition-colors hover:text-background/60"
                  onClick={() => setMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              <div className="grid grid-cols-2 border-b border-white/10">
                <Link
                  href="https://pypi.org/project/vlrdevapi/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-1.5 py-3.5 text-base font-medium tracking-tight text-background transition-colors hover:text-background/60 border-r border-white/10"
                  onClick={() => setMenuOpen(false)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M16 16v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4"/><path d="M8 8h4V4h4v4"/><rect x="2" y="14" width="8" height="6" rx="1"/><rect x="14" y="14" width="8" height="6" rx="1"/></svg>
                  <span>PyPI</span>
                </Link>
                <Link
                  href="https://github.com/vanshbordia/vlrdevapi"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-1.5 py-3.5 text-base font-medium tracking-tight text-background transition-colors hover:text-background/60"
                  onClick={() => setMenuOpen(false)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" clipRule="evenodd" d="M11.9317 1C5.91925 1 1 6.07047 1 12.2677C1 17.1973 4.14286 21.4227 8.51553 22.972C9.06211 23.1129 9.19876 22.6903 9.19876 22.4086C9.19876 22.1269 9.19876 21.4227 9.19876 20.4368C6.19255 21.141 5.50932 19.0283 5.50932 19.0283C4.96273 17.7607 4.2795 17.3382 4.2795 17.3382C3.32298 16.6339 4.41615 16.6339 4.41615 16.6339C5.50932 16.7748 6.0559 17.7607 6.0559 17.7607C7.01242 19.5917 8.65217 19.0283 9.19876 18.7466C9.3354 18.0424 9.6087 17.479 9.88199 17.1973C7.42236 16.9156 4.96273 15.9297 4.96273 11.5635C4.96273 10.2959 5.37267 9.30993 6.0559 8.6057C5.91925 8.32401 5.50932 7.19724 6.19255 5.64793C6.19255 5.64793 7.14907 5.36624 9.19876 6.7747C10.0186 6.49301 10.9752 6.35216 11.9317 6.35216C12.8882 6.35216 13.8447 6.49301 14.6646 6.7747C16.7143 5.36624 17.6708 5.64793 17.6708 5.64793C18.2174 7.19724 17.9441 8.32401 17.8075 8.6057C18.4907 9.45078 18.9006 10.4367 18.9006 11.5635C18.9006 15.9297 16.3043 16.7748 13.8447 17.0565C14.2547 17.6199 14.6646 18.3241 14.6646 19.31C14.6646 20.8593 14.6646 21.9861 14.6646 22.4086C14.6646 22.6903 14.8012 23.1129 15.4845 22.972C19.8571 21.4227 23 17.1973 23 12.2677C22.8634 6.07047 17.9441 1 11.9317 1Z" />
                  </svg>
                  <span>GitHub</span>
                </Link>
              </div>
            </nav>
            <div className="mt-5 flex flex-col gap-2">
              <Link
                href="/docs/"
                className="inline-flex items-center justify-center h-11 gap-1 font-medium tracking-tight px-5 text-base bg-background text-foreground hover:bg-white/90 transition-colors duration-200"
                onClick={() => setMenuOpen(false)}
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
