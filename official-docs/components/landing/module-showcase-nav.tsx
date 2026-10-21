'use client';

import { useEffect, useState, type MouseEvent } from 'react';

export type ModuleId = 'player' | 'team' | 'series' | 'event' | 'news';

export interface ModuleNavItem {
  id: ModuleId;
  label: string;
}

/**
 * Client-only navigation and scroll spy for the server-rendered module
 * showcase. Keeping this separate means the previews and code samples never
 * enter the client bundle.
 */
export function ModuleShowcaseNav({ items }: { items: ModuleNavItem[] }) {
  const [activeId, setActiveId] = useState<ModuleId>(items[0]?.id ?? 'player');
  const key = items.map((item) => item.id).join('|');

  useEffect(() => {
    const ids = key ? (key.split('|') as ModuleId[]) : [];
    const sections = ids
      .map((id) => document.getElementById(id))
      .filter((section): section is HTMLElement => section !== null);

    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) setActiveId(visible[0].target.id as ModuleId);
      },
      { rootMargin: '-18% 0px -58% 0px', threshold: [0, 0.15, 0.4] },
    );

    for (const section of sections) observer.observe(section);
    return () => observer.disconnect();
  }, [key]);

  function scrollToModule(event: MouseEvent<HTMLAnchorElement>, id: ModuleId) {
    event.preventDefault();
    setActiveId(id);
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.getElementById(id)?.scrollIntoView({
      behavior: reduceMotion ? 'auto' : 'smooth',
      block: 'start',
    });
    window.history.replaceState(null, '', `#${id}`);
  }

  return (
    <nav aria-label="API namespaces" className="mt-7 border-t border-white/10">
      {items.map((item, index) => {
        const active = item.id === activeId;

        return (
          <a
            key={item.id}
            href={`#${item.id}`}
            onClick={(event) => scrollToModule(event, item.id)}
            aria-current={active ? 'location' : undefined}
            className={`group flex items-center gap-3 border-b border-white/10 py-3.5 text-[13px] transition-colors ${
              active ? 'text-white' : 'text-white/40 hover:text-white/75'
            }`}
          >
            <span
              aria-hidden="true"
              className={`h-4 w-px transition-colors duration-300 ${
                active ? 'bg-[#ff4655]' : 'bg-white/10'
              }`}
            />
            <span className="font-mono text-[12px] text-white/25">
              {String(index + 1).padStart(2, '0')}
            </span>
            <span className="font-medium">{item.label}</span>
            <span
              aria-hidden="true"
              className={`ml-auto size-1 transition-all duration-300 ${
                active ? 'bg-[#ff4655] opacity-100' : 'bg-transparent opacity-0'
              }`}
            />
          </a>
        );
      })}
    </nav>
  );
}
