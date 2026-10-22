import { ContentCard } from '@/components/marketing/content-page';

export interface ContentIndexItem {
  slug: string;
  title: string;
  description: string;
  date: string;
}

export interface ContentIndexProps {
  /** Section label above the heading, e.g. `The index`. */
  label?: string;
  /** Heading, e.g. `All posts`. */
  title: string;
  /** Entries to list, newest first. */
  items: ContentIndexItem[];
  /** Route prefix, e.g. `/blog`. */
  basePath: string;
  /** Singular noun for the entry count, e.g. `post`. */
  itemNoun: string;
  /** Plural noun for the entry count, e.g. `posts`. Defaults to `${itemNoun}s`. */
  itemNounPlural?: string;
  /** Label on the card action, e.g. `Read post`. */
  actionLabel: string;
  /** Message shown when there are no entries. */
  emptyMessage: string;
  /** Responsive column count. */
  columns?: 'two' | 'three';
}

/**
 * The index block shared by the blog and guides listings.
 *
 * Both listings were near-identical copies; this keeps them in sync and
 * gives both the same card layout.
 */
export function ContentIndex({
  label = 'The index',
  title,
  items,
  basePath,
  itemNoun,
  itemNounPlural,
  actionLabel,
  emptyMessage,
  columns = 'two',
}: ContentIndexProps) {
  const plural = itemNounPlural ?? `${itemNoun}s`;

  return (
    <section>
      <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-4">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              {label}
            </p>
            <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              {title}
            </h2>
          </div>
          <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
            {items.length} {items.length === 1 ? itemNoun : plural}
          </span>
        </div>

        {items.length === 0 ? (
          <p className="mt-8 border border-white/10 bg-white/[0.02] p-5 text-[13px] text-white/50">
            {emptyMessage}
          </p>
        ) : (
          <div
            className={`mt-8 grid gap-3 sm:grid-cols-2${
              columns === 'three' ? ' lg:grid-cols-3' : ''
            }`}
          >
            {items.map((item, index) => (
              <ContentCard
                key={item.slug}
                href={`${basePath}/${item.slug}/`}
                index={String(index + 1).padStart(2, '0')}
                date={item.date}
                title={item.title}
                description={item.description}
                actionLabel={actionLabel}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
