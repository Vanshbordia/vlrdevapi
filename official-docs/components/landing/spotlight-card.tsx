'use client';

import Link from 'next/link';
import { useRef, type MouseEvent, type ReactNode } from 'react';

function setSpotlight(element: HTMLElement, clientX: number, clientY: number) {
  const rect = element.getBoundingClientRect();
  element.style.setProperty('--spotlight-x', `${clientX - rect.left}px`);
  element.style.setProperty('--spotlight-y', `${clientY - rect.top}px`);
}

function Glow() {
  return (
    <span
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      style={{
        background:
          'radial-gradient(340px circle at var(--spotlight-x, 50%) var(--spotlight-y, 0%), rgba(255,70,85,0.09), transparent 68%)',
      }}
    />
  );
}

export function SpotlightCard({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  function onMouseMove(event: MouseEvent<HTMLDivElement>) {
    if (ref.current) setSpotlight(ref.current, event.clientX, event.clientY);
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMouseMove}
      className={`group relative overflow-hidden border border-white/10 bg-[#080808] transition-colors duration-300 hover:border-white/25 ${className}`}
    >
      <Glow />
      <span aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 z-20 h-px overflow-hidden">
        <span className="block h-px w-1/3 -translate-x-full bg-gradient-to-r from-transparent via-[#ff4655]/80 to-transparent group-hover:animate-[landing-edge-run_1.1s_ease-out]" />
      </span>
      <span
        aria-hidden="true"
        className="absolute right-0 top-0 z-10 size-1.5 bg-[#ff4655] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
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
  const ref = useRef<HTMLAnchorElement>(null);

  function onMouseMove(event: MouseEvent<HTMLAnchorElement>) {
    if (ref.current) setSpotlight(ref.current, event.clientX, event.clientY);
  }

  return (
    <Link
      ref={ref}
      href={href}
      onMouseMove={onMouseMove}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      className={`group relative flex overflow-hidden border border-white/10 bg-[#080808] transition-colors duration-300 hover:border-white/25 hover:bg-white/[0.02] ${className}`}
    >
      <Glow />
      <span aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 z-20 h-px overflow-hidden">
        <span className="block h-px w-1/3 -translate-x-full bg-gradient-to-r from-transparent via-[#ff4655]/80 to-transparent group-hover:animate-[landing-edge-run_1.1s_ease-out]" />
      </span>
      <span
        aria-hidden="true"
        className="absolute right-0 top-0 z-10 size-1.5 bg-[#ff4655] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      />
      <div className="relative flex w-full flex-1 flex-col">{children}</div>
    </Link>
  );
}
