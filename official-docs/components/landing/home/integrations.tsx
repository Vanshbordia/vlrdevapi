import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { Reveal } from '@/components/landing/reveal';

const guides = [
  {
    title: 'Getting started with VLRdevAPI',
    description: 'From an empty project to a first typed response.',
    href: '/guides/getting-started-with-vlrdevapi',
  },
  {
    title: 'Building a real-time match monitor',
    description: 'Poll live matches, track the score, and fire an alert.',
    href: '/guides/building-a-real-time-match-monitor',
  },
  {
    title: 'Building a Valorant esports Discord bot',
    description: 'Slash commands for fixtures, rosters, and live scores.',
    href: '/guides/building-a-valorant-esports-discord-bot',
  },
  {
    title: 'Player analytics with pandas',
    description: 'Turn agent and match stats into a DataFrame.',
    href: '/guides/player-analytics-with-pandas',
  },
  {
    title: 'Event analytics with Polars',
    description: 'Break a tournament down by placement and prize money.',
    href: '/guides/event-analytics-with-polars',
  },
];

const reference = [
  {
    title: 'Getting started',
    description: 'Install the package and make your first call.',
    href: '/docs/getting-started',
  },
  {
    title: 'Quickstart',
    description: 'A runnable tour of the namespaces.',
    href: '/docs/quickstart',
  },
  {
    title: 'API reference',
    description: 'Every namespace, method, and response model.',
    href: '/docs/reference',
  },
];

/** Guides and documentation entry points. */
export function Integrations() {
  return (
    <section className="border-b border-white/10">
      <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
        <Reveal className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-2xl">
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">
              Guides &amp; reference
            </p>
            <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl">
              Start from a recipe,
              <br />
              <span className="text-fd-muted">stay for the reference.</span>
            </h2>
          </div>
          <Link
            href="/guides/"
            className="group inline-flex items-center gap-1.5 pb-1 text-[12.5px] font-medium text-white/60 transition-colors hover:text-white"
          >
            All guides
            <ArrowUpRight
              className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        </Reveal>

        <div className="mt-12 grid gap-10 lg:grid-cols-[1.35fr_0.65fr] lg:gap-16">
          <Reveal>
            <h3 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              Tutorials
            </h3>
            <ul className="mt-5 border-t border-white/10">
              {guides.map((guide) => (
                <li key={guide.href} className="border-b border-white/10">
                  <Link
                    href={guide.href}
                    className="group flex items-start justify-between gap-6 py-4"
                  >
                    <span className="min-w-0">
                      <span className="block text-[15px] font-medium tracking-tight text-white/85 transition-colors group-hover:text-white">
                        {guide.title}
                      </span>
                      <span className="mt-1 block text-[13px] leading-relaxed text-fd-muted">
                        {guide.description}
                      </span>
                    </span>
                    <ArrowUpRight
                      className="mt-1 size-3.5 shrink-0 text-white/20 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-fd-primary"
                      aria-hidden="true"
                    />
                  </Link>
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal delay={70}>
            <h3 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              Documentation
            </h3>
            <ul className="mt-5 border-t border-white/10">
              {reference.map((entry) => (
                <li key={entry.href} className="border-b border-white/10">
                  <Link
                    href={entry.href}
                    className="group flex items-start justify-between gap-6 py-4"
                  >
                    <span className="min-w-0">
                      <span className="block text-[15px] font-medium tracking-tight text-white/85 transition-colors group-hover:text-white">
                        {entry.title}
                      </span>
                      <span className="mt-1 block text-[13px] leading-relaxed text-fd-muted">
                        {entry.description}
                      </span>
                    </span>
                    <ArrowUpRight
                      className="mt-1 size-3.5 shrink-0 text-white/20 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-fd-primary"
                      aria-hidden="true"
                    />
                  </Link>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
