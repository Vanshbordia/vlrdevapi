'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';

/**
 * Surfaces used across the marketing pages.
 *
 * Deliberately plain: a hairline border on the panel colour, and a red hairline
 * that draws in on hover. No glow, no pointer tracking, no edge animation.
 */
export function SpotlightCard({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`group relative overflow-hidden border border-white/10 bg-fd-panel transition-colors duration-300 hover:border-white/20 ${className}`}
    >
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
      />
      <div className="relative">{children}</div>
    </div>
  );
}

export function SpotlightLink({
  href,
  external = false,
  children,
  className = '',
}: {
  href: string;
  external?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Link
      href={href}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      className={`group relative flex overflow-hidden border border-white/10 bg-fd-panel transition-colors duration-300 hover:border-white/20 hover:bg-fd-raised ${className}`}
    >
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
      />
      <div className="relative flex w-full flex-1 flex-col">{children}</div>
    </Link>
  );
}
