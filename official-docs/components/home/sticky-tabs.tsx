'use client';

import { useEffect, useState } from 'react';

const sections = [
  { id: 'install', label: 'Install' },
  { id: 'import', label: 'Import' },
  { id: 'configure', label: 'Configure' },
  { id: 'fetch', label: 'Fetch' },
  { id: 'build', label: 'Build' },
];

export function StickyTabs() {
  const [active, setActive] = useState('install');

  useEffect(() => {
    const observers: IntersectionObserver[] = [];
    for (const { id } of sections) {
      const el = document.getElementById(id);
      if (!el) continue;
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) setActive(id);
        },
        { rootMargin: '-112px 0px -60% 0px' },
      );
      observer.observe(el);
      observers.push(observer);
    }
    return () => observers.forEach((o) => o.disconnect());
  }, []);

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <nav aria-label="Steps" className="h-full">
      <ul className="grid h-full min-w-[41.25rem] grid-cols-5 md:w-full md:min-w-0">
        {sections.map((s, i) => (
          <li key={s.id}>
            <a
              href={`#${s.id}`}
              onClick={(e) => handleClick(e, s.id)}
              className={`relative flex h-full w-full items-center justify-center border-t border-l border-border px-3 text-base leading-[1.125] font-normal transition-colors sm:px-4 sm:text-lg md:text-[1.125rem] lg:text-xl overflow-hidden ${i === 4 ? 'border-r' : ''} ${active === s.id ? 'text-foreground bg-fd-primary/10' : 'text-muted-foreground'}`}
            >
              {s.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
