'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowUpRight } from 'lucide-react';

const links = [
  { href: '/docs/', label: 'Docs' },
  { href: '/guides/', label: 'Guides' },
  { href: '/blog/', label: 'Blog' },
  { href: '/faq/', label: 'FAQ' },
  { href: '/changelog/', label: 'Changelog' },
];

/**
 * The primary navigation links.
 *
 * Client-side only because the active route depends on `usePathname()`. The
 * links themselves are static, so this island is as small as it can be.
 */
export function SiteNavLinks() {
  const pathname = usePathname();
  const normalizedPath = pathname.endsWith('/') ? pathname : `${pathname}/`;

  return (
    <>
      {links.map((link) => {
        const active = normalizedPath.startsWith(link.href);

        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={active ? 'page' : undefined}
            className={`group relative px-3.5 py-1.5 text-[13.5px] font-medium transition-colors hover:text-white ${
              active ? 'text-white' : 'text-white/70'
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
    </>
  );
}

/**
 * The header's primary CTA. Split out so the shell can stay a Server
 * Component; it only needs the active route for the hover treatment.
 */
export function DocsCtaLink() {
  const pathname = usePathname();
  const active = (pathname.endsWith('/') ? pathname : `${pathname}/`).startsWith('/docs');

  return (
    <Link
      href="/docs/"
      className={`group inline-flex h-9 items-center gap-1.5 border px-4 text-[13.5px] font-medium transition-colors ${
        active
          ? 'border-[#ff4655] bg-[#ff4655] text-white'
          : 'border-white bg-white text-black hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white'
      }`}
    >
      Read the docs
      <ArrowUpRight
        className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
        aria-hidden="true"
      />
    </Link>
  );
}
