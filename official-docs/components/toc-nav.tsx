'use client';

import type { TocItem } from './toc';
import { useActiveId } from './use-active-id';

export function TocNav({ items }: { items: TocItem[] }) {
  const activeId = useActiveId(items.map((item) => item.id));

  return (
    <>
      <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
        On this page
      </h2>
      {items.length === 0 ? (
        <p className="mt-4 border-l border-white/10 pl-4 text-[12px] text-fd-muted">
          No sections
        </p>
      ) : (
        <ol className="mt-4 border-l border-white/10">
          {items.map((item) => {
            const isActive = activeId === item.id;

            return (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  aria-current={isActive ? 'location' : undefined}
                  className={`-ml-px block border-l py-1.5 leading-snug transition-colors ${
                    isActive
                      ? 'border-[#ff4655] text-white'
                      : 'border-transparent text-fd-muted hover:border-[#ff4655]/40 hover:text-white'
                  } ${item.level > 2 ? 'pl-7 text-[12px]' : 'pl-4 text-[12.5px]'}`}
                >
                  {item.text}
                </a>
              </li>
            );
          })}
        </ol>
      )}
    </>
  );
}
