import type { ReactNode } from 'react';
import type { TocItem } from './toc';
import { TocNav } from './toc-nav';

interface TocLayoutProps {
  children: ReactNode;
  items: TocItem[];
}

export function TocLayout({ children, items }: TocLayoutProps) {
  return (
    <div className="grid grid-cols-1 gap-12 lg:grid-cols-[minmax(0,1fr)_220px] lg:gap-16">
      <div className="min-w-0">{children}</div>
      <aside className="hidden lg:block">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <TocNav items={items} />
        </div>
      </aside>
    </div>
  );
}
