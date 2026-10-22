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
  Trophy,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

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

/**
 * The "Why" disclosure in the header.
 *
 * Opens on click as well as hover, closes on Escape (returning focus to the
 * trigger), and exposes `role="menu"` / `role="menuitem"` so keyboard users
 * can tell it is a menu.
 */
export function WhyMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const pathname = usePathname();
  const normalizedPath = pathname.endsWith('/') ? pathname : `${pathname}/`;
  const active = whyPages.some((link) => normalizedPath.startsWith(link.href));

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      if (!ref.current?.contains(event.target as Node)) setOpen(false);
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      setOpen(false);
      triggerRef.current?.focus();
    };

    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  return (
    <div
      ref={ref}
      className="relative"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => {
        const panel = ref.current?.querySelector('#why-menu');
        if (panel?.contains(document.activeElement)) return;
        setOpen(false);
      }}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
          setOpen(false);
        }
      }}
    >
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls="why-menu"
        onClick={() => setOpen((value) => !value)}
        className={`group relative inline-flex items-center gap-1.5 px-3.5 py-1.5 text-[13.5px] font-medium transition-colors hover:text-white ${
          active ? 'text-white' : 'text-white/70'
        }`}
      >
        Why
        <ChevronDown
          aria-hidden="true"
          className={`size-3.5 transition-transform duration-200 ${open ? 'rotate-180 text-[#ff8d97]' : ''}`}
        />
        <span
          aria-hidden="true"
          className={`absolute inset-x-3.5 bottom-0.5 h-px origin-left bg-[#ff4655] transition-transform duration-200 group-hover:scale-x-100 ${
            active ? 'scale-x-100' : 'scale-x-0'
          }`}
        />
      </button>

      {open ? (
        <div className="absolute right-0 top-full z-50 pt-4">
          <div
            id="why-menu"
            role="menu"
            aria-label="Why VLRdevAPI"
            className="w-[480px] max-w-[calc(100vw-2rem)] border border-white/10 bg-black shadow-2xl shadow-black/60"
          >
            <div className="grid grid-cols-2">
              {whyPages.map((link, index) => {
                const Icon = link.icon;

                return (
                  <Link
                    key={link.href}
                    role="menuitem"
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className={`group relative flex h-full flex-col gap-2.5 p-4 transition-colors hover:bg-white/[0.03] ${
                      index % 2 === 1 ? 'border-l border-white/10' : ''
                    } ${index >= 2 ? 'border-t border-white/10' : ''}`}
                  >
                    <span className="flex size-8 items-center justify-center border border-white/10 text-white/65 transition-colors group-hover:border-[#ff4655]/40 group-hover:text-[#ff8d97]">
                      <Icon className="size-4" aria-hidden="true" />
                    </span>
                    <span className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-white/90 transition-colors group-hover:text-white">
                        {link.label}
                      </span>
                      <span className="text-[12px] leading-relaxed text-white/55">
                        {link.description}
                      </span>
                    </span>
                  </Link>
                );
              })}
            </div>

            <div className="border-t border-white/10 p-2">
              <p className="px-2 pb-1 pt-0.5 font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                Compare
              </p>
              <div className="grid grid-cols-2 gap-1">
                {whyComparisons.map((link) => {
                  const Icon = link.icon;

                  return (
                    <Link
                      key={link.href}
                      role="menuitem"
                      href={link.href}
                      onClick={() => setOpen(false)}
                      className="group flex items-center gap-2 p-2.5 text-[12.5px] text-white/65 transition-colors hover:bg-white/[0.03] hover:text-white"
                    >
                      <Icon
                        className="size-3.5 shrink-0 text-fd-muted transition-colors group-hover:text-[#ff8d97]"
                        aria-hidden="true"
                      />
                      <span className="min-w-0">
                        <span className="block">{link.label}</span>
                        <span className="mt-0.5 block text-[12px] leading-snug text-fd-muted">
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
  );
}
