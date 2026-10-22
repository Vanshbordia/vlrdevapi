import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import type { ReactNode } from 'react';

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
});

export function formatDate(value: string) {
  const parsed = new Date(`${value}T00:00:00Z`);

  if (Number.isNaN(parsed.getTime())) return value;

  return dateFormatter.format(parsed);
}

export function ContentHero({
  eyebrow,
  title,
  description,
  aside,
  children,
}: {
  eyebrow: string;
  title: ReactNode;
  description: string;
  aside?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <section className="relative overflow-hidden border-b border-white/10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_55%_55%_at_82%_-10%,rgba(255,70,85,0.14),transparent_70%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-50 [background-image:linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_85%_65%_at_50%_0%,black,transparent_78%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-0 h-px w-[min(92vw,72rem)] -translate-x-1/2 bg-gradient-to-r from-transparent via-fd-primary/60 to-transparent"
      />
      <div
        className={`relative mx-auto w-full px-5 pb-16 pt-14 sm:px-8 sm:pb-20 sm:pt-20 ${
          aside
            ? 'grid max-w-7xl gap-12 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-end lg:gap-16 lg:pb-24 lg:pt-24'
            : 'max-w-7xl'
        }`}
      >
        <div className="min-w-0">
          <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">
            {eyebrow}
          </p>
          <h1 className="mt-5 max-w-4xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.8rem] lg:text-[4.4rem]">
            {title}
          </h1>
          <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-white/50 sm:text-base">
            {description}
          </p>
          {children ? <div className="mt-8 flex flex-wrap items-center gap-3">{children}</div> : null}
        </div>
        {aside ? <div className="min-w-0">{aside}</div> : null}
      </div>
    </section>
  );
}

export function ArticleHero({
  backHref,
  backLabel,
  kind,
  date,
  title,
  description,
}: {
  backHref: string;
  backLabel: string;
  kind: string;
  date: string;
  title: string;
  description?: string;
}) {
  return (
    <section className="relative overflow-hidden border-b border-white/10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_60%_at_78%_-12%,rgba(255,70,85,0.13),transparent_72%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_85%_65%_at_50%_0%,black,transparent_78%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-0 h-px w-[min(92vw,72rem)] -translate-x-1/2 bg-gradient-to-r from-transparent via-fd-primary/60 to-transparent"
      />
      <div className="relative mx-auto w-full max-w-5xl px-5 pb-14 pt-14 sm:px-8 sm:pb-16 sm:pt-20">
        <Link
          href={backHref}
          className="inline-flex items-center gap-2 font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted transition-colors hover:text-white"
        >
          <span aria-hidden="true" className="h-px w-4 bg-fd-primary/70" />
          {backLabel}
        </Link>
        <div className="mt-8 flex flex-wrap items-center gap-3 font-mono text-[12px] uppercase tracking-[0.14em]">
          <span className="text-fd-primary">{kind}</span>
          <span aria-hidden="true" className="text-white/20">
            /
          </span>
          <time dateTime={date} className="text-fd-muted">
            {formatDate(date)}
          </time>
        </div>
        <h1 className="mt-5 max-w-4xl text-[2.5rem] font-medium leading-[1.02] tracking-[-0.04em] text-white sm:text-[3.4rem] lg:text-[3.9rem]">
          {title}
        </h1>
        {description ? (
          <p className="mt-5 max-w-3xl text-[15px] leading-relaxed text-white/50 sm:text-base">
            {description}
          </p>
        ) : null}
      </div>
    </section>
  );
}

export function IndexPanel({
  label,
  rows,
  note,
}: {
  label: string;
  rows: Array<{ label: string; value: ReactNode }>;
  note?: ReactNode;
}) {
  return (
    <div className="border border-white/10 bg-fd-panel">
      <div className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-3">
        <span className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
          {label}
        </span>
        <span aria-hidden="true" className="size-1.5 bg-fd-primary" />
      </div>
      <dl className="divide-y divide-white/10">
        {rows.map((row) => (
          <div key={row.label} className="flex items-center justify-between gap-5 px-4 py-3">
            <dt className="font-mono text-[12px] uppercase tracking-[0.12em] text-fd-muted">
              {row.label}
            </dt>
            <dd className="truncate text-right font-mono text-[12.5px] text-white/65">
              {row.value}
            </dd>
          </div>
        ))}
      </dl>
      {note ? (
        <div className="border-t border-white/10 px-4 py-3 text-[12px] leading-relaxed text-fd-muted">
          {note}
        </div>
      ) : null}
    </div>
  );
}

export function ContentCard({
  href,
  index,
  date,
  title,
  description,
  actionLabel,
}: {
  href: string;
  index: string;
  date: string;
  title: string;
  description: string;
  actionLabel: string;
}) {
  return (
    <Link
      href={href}
      className="group relative flex h-full flex-col overflow-hidden border border-white/10 bg-fd-panel p-5 transition-colors hover:border-white/20"
    >
      <span
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
      />
      <div className="flex items-center justify-between gap-4 font-mono text-[12px] uppercase tracking-[0.14em]">
        <span className="text-fd-primary">{index}</span>
        <time dateTime={date} className="text-fd-muted">
          {formatDate(date)}
        </time>
      </div>
      <h3 className="mt-6 text-lg font-medium leading-snug tracking-tight text-white/85 transition-colors group-hover:text-white">
        {title}
      </h3>
      <p className="mt-3 line-clamp-3 text-[13.5px] leading-relaxed text-fd-muted">
        {description}
      </p>
      <span className="mt-auto inline-flex items-center gap-1.5 pt-6 text-[12px] font-medium text-fd-muted transition-colors group-hover:text-fd-primary">
        {actionLabel}
        <ArrowUpRight
          className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
          aria-hidden="true"
        />
      </span>
    </Link>
  );
}

export function RelatedLinks({
  links,
  title = 'Related',
}: {
  links: Array<{ href: string; label: string }>;
  title?: string;
}) {
  return (
    <section className="border-t border-white/10">
      <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8">
        <div className="flex items-center gap-4">
          <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
            {title}
          </h2>
          <span aria-hidden="true" className="h-px flex-1 bg-white/10" />
        </div>
        <ul className="mt-6 flex flex-wrap gap-2">
          {links.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="group inline-flex items-center gap-2 border border-white/10 px-4 py-2.5 text-[13px] text-white/50 transition-colors hover:border-fd-primary/50 hover:text-white"
              >
                {link.label}
                <ArrowUpRight
                  className="size-3 text-white/20 transition-colors group-hover:text-fd-primary"
                  aria-hidden="true"
                />
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
