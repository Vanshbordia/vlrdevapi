'use client';

import type { ReactNode } from 'react';
import { useActiveId } from '@/components/use-active-id';

export interface AnchorNavItem {
  id: string;
  label: string;
  meta?: string;
}

interface AnchorNavProps {
  label: string;
  ariaLabel: string;
  items: AnchorNavItem[];
  variant?: 'inline' | 'stacked';
  note?: ReactNode;
}

/**
 * Client-only scroll spy for server-rendered anchor sections. The content
 * itself stays on the server; only the active-link state hydrates.
 */
export function AnchorNav({
  label,
  ariaLabel,
  items,
  variant = 'inline',
  note,
}: AnchorNavProps) {
  const activeId = useActiveId(items.map((item) => item.id));
  const stacked = variant === 'stacked';

  return (
    <>
      <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
        {label}
      </p>
      <nav aria-label={ariaLabel} className="mt-4">
        <ol className="border-l border-white/10">
          {items.map((item) => {
            const isActive = activeId === item.id;

            return (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  aria-current={isActive ? 'location' : undefined}
                  className={`group -ml-px flex border-l py-2.5 pl-4 transition-colors ${
                    stacked ? 'flex-col gap-1' : 'items-center gap-3'
                  } ${
                    isActive
                      ? 'border-[#ff4655] text-white'
                      : 'border-transparent text-white/40 hover:text-white/75'
                  }`}
                >
                  {item.meta ? (
                    <span
                      className={
                        stacked
                          ? 'font-mono text-[12px] uppercase tracking-[0.12em] text-[#ff8d97]'
                          : 'font-mono text-[12px] text-white/25'
                      }
                    >
                      {item.meta}
                    </span>
                  ) : null}
                  <span className={stacked ? 'text-[13px] font-medium' : 'text-[13px]'}>
                    {item.label}
                  </span>
                </a>
              </li>
            );
          })}
        </ol>
      </nav>
      {note ? (
        <div className="mt-6 border-t border-white/10 pt-4 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
          {note}
        </div>
      ) : null}
    </>
  );
}
