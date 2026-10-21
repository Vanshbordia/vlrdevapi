import type { Metadata } from 'next';
import Link from 'next/link';
import {
  ArrowRight,
  ArrowUpRight,
  Boxes,
  Clock3,
  Gauge,
  Layers,
  Workflow,
} from 'lucide-react';
import { canonicalUrl, siteUrl } from '@/lib/shared';
import { project, projectAuthor, projectSameAs, projectUrls } from '@/lib/project';
import { ParallelDemo, TimezoneDemo, TypedFieldsDemo } from '@/components/landing/bento-demos';
import { CopyCommand } from '@/components/landing/copy-command';
import { CountUp } from '@/components/landing/count-up';
import { CurriedDemo } from '@/components/landing/curried-demo';
import { RateLimitDemo } from '@/components/landing/rate-limit-demo';
import { Faq } from '@/components/landing/faq';
import { GithubIcon } from '@/components/landing/github-icon';
import { HeroDemo } from '@/components/landing/hero-demo';
import { ModuleShowcase } from '@/components/landing/module-showcase';
import { Reveal } from '@/components/landing/reveal';
import { SpotlightCard, SpotlightLink } from '@/components/landing/spotlight-card';

export const metadata: Metadata = {
  alternates: { canonical: canonicalUrl('/') },
};

const jsonLdSoftwareApp = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  '@id': `${projectUrls.home}#software`,
  name: project.name,
  url: projectUrls.home,
  description: project.description,
  applicationCategory: 'DeveloperApplication',
  applicationSubCategory: 'Esports data SDK',
  operatingSystem: project.runtimePlatform,
  programmingLanguage: project.programmingLanguage,
  softwareVersion: project.version,
  license: project.licenseUrl,
  isAccessibleForFree: true,
  softwareHelp: projectUrls.docs,
  downloadUrl: project.packageUrl,
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  author: projectAuthor,
  publisher: { '@id': `${siteUrl}/#organization` },
  sameAs: projectSameAs,
};

const useCases = [
  'Discord bots',
  'Live dashboards',
  'Analytics notebooks',
  'Fantasy leagues',
  'Scouting tools',
  'Match alerts',
  'ML pipelines',
  'Content platforms',
];

const stats: Array<{
  value?: string;
  count?: number;
  suffix?: string;
  label: string;
  detail: string;
}> = [
  { value: '0', label: 'API keys to manage', detail: 'No signup. No secrets.' },
  { count: 6, label: 'Typed namespaces', detail: 'Players through news.' },
  {
    count: 100,
    suffix: '%',
    label: 'Modeled responses',
    detail: 'Pydantic, all the way down.',
  },
  { value: 'MIT', label: 'Open-source license', detail: 'Build on it. Ship it.' },
];

const stack = [
  {
    name: 'pandas',
    tag: 'Player analytics',
    description: 'Turn player and agent stats into DataFrames for notebooks and reports.',
    href: '/guides/player-analytics-with-pandas/',
  },
  {
    name: 'Polars',
    tag: 'Event analytics',
    description: 'Wrangle tournament-wide match data at speed with a Polars workflow.',
    href: '/guides/event-analytics-with-polars/',
  },
  {
    name: 'discord.py',
    tag: 'Discord bot',
    description: 'Ship slash commands for live scores, rosters, and match lookups.',
    href: '/guides/building-a-valorant-esports-discord-bot/',
  },
  {
    name: 'Workers',
    tag: 'Live monitor',
    description: 'Poll upcoming matches and trigger alerts when a series goes live.',
    href: '/guides/building-a-real-time-match-monitor/',
  },
];

const resources = [
  {
    index: '01',
    title: 'Getting started',
    tag: 'Documentation',
    description: 'Install the package, make your first call, and learn the core client patterns.',
    href: '/docs/getting-started/',
  },
  {
    index: '02',
    title: 'API reference',
    tag: 'Every field',
    description: 'Browse each namespace, method, and typed response model with examples.',
    href: '/docs/reference/',
  },
  {
    index: '03',
    title: 'Guides',
    tag: 'Build something',
    description: 'Discord bots, live monitors, pandas notebooks, and Polars pipelines.',
    href: '/guides/',
  },
];

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdSoftwareApp).replace(/</g, '\\u003c'),
        }}
      />
      <main id="main" tabIndex={-1} className="flex-1 bg-black text-white">
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-white/10">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 animate-[landing-glow_9s_ease-in-out_infinite] bg-[radial-gradient(ellipse_55%_55%_at_82%_-5%,rgba(255,70,85,0.16),transparent_70%)]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 animate-[landing-grid-drift_24s_linear_infinite] opacity-50 [background-image:linear-gradient(to_right,rgba(255,255,255,0.045)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.045)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_85%_65%_at_50%_0%,black,transparent_75%)]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute left-1/2 top-0 h-px w-[min(92vw,72rem)] -translate-x-1/2 bg-gradient-to-r from-transparent via-[#ff4655]/60 to-transparent"
          />
          <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-14 sm:px-8 sm:pb-20 sm:pt-20 lg:pb-24 lg:pt-24">
            <div className="grid items-center gap-14 lg:grid-cols-[1.02fr_0.98fr] lg:gap-12 xl:gap-20">
              <div>
                <Reveal>
                  <div className="inline-flex items-center gap-2 border border-white/15 bg-white/[0.02] py-1 pl-1 pr-3 font-mono text-[12px] uppercase tracking-[0.14em] text-white/45">
                    <span className="bg-[#ff4655] px-1.5 py-0.5 text-[12px] font-semibold tracking-[0.1em] text-black">
                      v{project.version}
                    </span>
                    Typed Python SDK · no API key
                  </div>
                </Reveal>

                <h1 className="mt-6 text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.8rem] lg:text-[4.15rem] xl:text-[4.8rem]">
                  <span className="landing-enter block" style={{ animationDelay: '40ms' }}>
                    The Valorant
                  </span>
                  <span
                    className="landing-enter block text-[#ff4655]"
                    style={{ animationDelay: '120ms' }}
                  >
                    data layer
                  </span>
                  <span className="landing-enter block" style={{ animationDelay: '200ms' }}>
                    for Python
                  </span>
                </h1>

                <Reveal delay={140}>
                  <p className="mt-7 max-w-lg text-[15px] leading-relaxed text-white/50 sm:text-base">
                    A fully typed Python SDK for Valorant esports. Pull live matches, player stats,
                    rosters, brackets, round data, and news from VLR.gg — without writing a parser.
                  </p>
                </Reveal>

                <Reveal
                  delay={210}
                  className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center"
                >
                  <Link
                    href="/docs/"
                    className="group inline-flex h-11 items-center justify-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
                  >
                    Read the docs
                    <ArrowUpRight
                      className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                      aria-hidden="true"
                    />
                  </Link>
                  <CopyCommand command="pip install vlrdevapi" />
                </Reveal>

                <Reveal delay={260}>
                  <p className="mt-6 flex items-start gap-2.5 font-mono text-[12px] uppercase leading-relaxed tracking-[0.12em] text-white/35">
                    <span aria-hidden="true" className="mt-2 h-px w-5 shrink-0 bg-[#ff4655]/70" />
                    <span>Used by multiple Tier 1, Tier 2, and Game Changers teams</span>
                  </p>
                </Reveal>
              </div>

              <Reveal delay={160} className="relative min-w-0">
                <HeroDemo />
              </Reveal>
            </div>
          </div>
        </section>

        {/* Use cases */}
        <section aria-label="What people build with VLRdevAPI" className="border-b border-white/10 bg-white/[0.01]">
          <div className="mx-auto flex w-full max-w-7xl items-center gap-5 px-5 py-4 sm:px-8">
            <span className="hidden shrink-0 font-mono text-[12px] uppercase tracking-[0.18em] text-white/30 sm:inline-flex">
              Built for
            </span>
            <div className="relative min-w-0 flex-1 overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_9%,black_91%,transparent)]">
              <div
                aria-hidden="true"
                className="flex w-max animate-[landing-marquee_28s_linear_infinite] items-center hover:[animation-play-state:paused]"
              >
                {[0, 1].map((group) => (
                  <div key={group} className="flex shrink-0 items-center">
                    {useCases.map((item) => (
                      <span
                        key={`${group}-${item}`}
                        className="flex shrink-0 items-center whitespace-nowrap text-[13px] font-medium tracking-[-0.01em] text-white/40"
                      >
                        <span aria-hidden="true" className="mx-5 font-mono text-[12px] text-[#ff4655]/60">
                          /
                        </span>
                        {item}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </div>
            <Link
              href="/guides/"
              className="group hidden shrink-0 items-center gap-1.5 border-l border-white/10 pl-5 font-mono text-[12px] uppercase tracking-[0.16em] text-white/35 transition-colors hover:text-white md:inline-flex"
            >
              Use cases
              <ArrowUpRight
                className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>
        </section>

        {/* Stats */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
            <Reveal>
              <p className="mb-8 font-mono text-[12px] uppercase tracking-[0.2em] text-white/30">
                By the numbers
              </p>
            </Reveal>
            <Reveal className="grid grid-cols-2 border-l border-t border-white/10 lg:grid-cols-4">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="group relative border-b border-r border-white/10 p-5 transition-colors hover:bg-white/[0.02] sm:p-7"
                >
                  <span
                    aria-hidden="true"
                    className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-[#ff4655] transition-transform duration-500 group-hover:scale-x-100"
                  />
                  <p className="font-mono text-[2.6rem] font-medium leading-none tracking-[-0.06em] text-white tabular-nums sm:text-6xl lg:text-[4.4rem]">
                    {stat.count !== undefined ? (
                      <CountUp value={stat.count} suffix={stat.suffix} />
                    ) : (
                      stat.value
                    )}
                  </p>
                  <p className="mt-5 text-[13px] font-medium text-white/70">{stat.label}</p>
                  <p className="mt-1 text-[12px] text-white/30">{stat.detail}</p>
                </div>
              ))}
            </Reveal>
          </div>
        </section>

        {/* Features */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
            <Reveal className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-white/35">
                  Why VLRdevAPI
                </p>
                <h2 className="mt-4 max-w-2xl text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl lg:text-[2.9rem]">
                  Built to remove
                  <br />
                  <span className="text-white/35">the boring parts.</span>
                </h2>
              </div>
              <p className="max-w-md text-[14.5px] leading-relaxed text-white/45 lg:justify-self-end lg:pb-1">
                No HTML parsing. No stale selectors. No glue code between VLR.gg and your app. Just
                import the client and query the data you came for.
              </p>
            </Reveal>

            <div className="mt-10 grid gap-3 lg:grid-cols-12">
              {/* Typed models */}
              <Reveal className="lg:col-span-7">
                <SpotlightCard className="h-full p-6 sm:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                        Typed models
                      </p>
                      <h3 className="mt-3 text-lg font-medium tracking-tight text-white sm:text-xl">
                        No more dict.get(&quot;name&quot;)
                      </h3>
                      <p className="mt-2 max-w-md text-[13px] leading-relaxed text-white/40">
                        Every response is a Pydantic model with real fields, types, and descriptions.
                        Autocomplete works. Validation is free.
                      </p>
                    </div>
                    <Layers className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                  </div>
                  <TypedFieldsDemo />
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {['Field types', 'IDE autocomplete', 'Runtime validation', 'JSON schema'].map(
                      (item) => (
                        <span
                          key={item}
                          className="border border-white/10 px-2.5 py-1 font-mono text-[12px] text-white/35"
                        >
                          {item}
                        </span>
                      ),
                    )}
                  </div>
                </SpotlightCard>
              </Reveal>

              {/* Curried access */}
              <Reveal delay={70} className="lg:col-span-5">
                <SpotlightCard className="h-full p-6 sm:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                        Curried access
                      </p>
                      <h3 className="mt-3 text-lg font-medium tracking-tight text-white sm:text-xl">
                        Bind once, query anywhere
                      </h3>
                      <p className="mt-2 text-[13px] leading-relaxed text-white/40">
                        Pass an ID one time. Every related method hangs off the object you get back.
                      </p>
                    </div>
                    <Boxes className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                  </div>
                  <CurriedDemo />
                  <p className="mt-4 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                    One ID · every related surface
                  </p>
                </SpotlightCard>
              </Reveal>

              {/* Rate limits */}
              <Reveal className="lg:col-span-4">
                <SpotlightCard className="h-full p-6 sm:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                        Rate limiting
                      </p>
                      <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                        A good citizen by default
                      </h3>
                    </div>
                    <Gauge className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                  </div>
                  <p className="mt-2 text-[12.5px] leading-relaxed text-white/40">
                    Three requests per second out of the box, with retries and exponential backoff.
                  </p>
                  <RateLimitDemo />
                </SpotlightCard>
              </Reveal>

              {/* Parallel */}
              <Reveal delay={60} className="lg:col-span-4">
                <SpotlightCard className="h-full p-6 sm:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                        Concurrency
                      </p>
                      <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                        Parallel where it counts
                      </h3>
                    </div>
                    <Workflow className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                  </div>
                  <p className="mt-2 text-[12.5px] leading-relaxed text-white/40">
                    Multi-stage endpoints fetch their pages in parallel with a thread pool.
                  </p>
                  <ParallelDemo />
                  <p className="mt-4 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                    3 pages · one wait
                  </p>
                </SpotlightCard>
              </Reveal>

              {/* Timezone */}
              <Reveal delay={120} className="lg:col-span-4">
                <SpotlightCard className="h-full p-6 sm:p-7">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                        Timezones
                      </p>
                      <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                        Timezones, handled
                      </h3>
                    </div>
                    <Clock3 className="size-5 shrink-0 text-white/20" aria-hidden="true" />
                  </div>
                  <p className="mt-2 text-[12.5px] leading-relaxed text-white/40">
                    VLR.gg renders times for a viewer. Set source_tz once and dates come back
                    UTC-aware.
                  </p>
                  <TimezoneDemo />
                </SpotlightCard>
              </Reveal>
            </div>
          </div>
        </section>

        {/* Namespace showcase */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
            <ModuleShowcase />
          </div>
        </section>

        {/* Stack */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
            <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
              <Reveal>
                <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-white/35">
                  Integrations
                </p>
                <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl">
                  Plays well with
                  <br />
                  <span className="text-white/35">your stack.</span>
                </h2>
                <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-white/40">
                  The output is plain Pydantic models, so it drops straight into notebooks,
                  services, bots, and background workers.
                </p>
                <Link
                  href="/guides/"
                  className="group mt-6 inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
                >
                  Browse all guides
                  <ArrowRight
                    className="size-3.5 transition-transform duration-200 group-hover:translate-x-0.5"
                    aria-hidden="true"
                  />
                </Link>
              </Reveal>

              <Reveal className="grid gap-3 sm:grid-cols-2">
                {stack.map((item) => (
                  <SpotlightLink
                    key={item.name}
                    href={item.href}
                    className="min-h-[190px] p-5"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/30">
                        {item.tag}
                      </span>
                      <ArrowUpRight
                        className="size-3.5 text-white/25 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-white/60"
                        aria-hidden="true"
                      />
                    </div>
                    <h3 className="mt-6 text-lg font-medium tracking-tight text-white">
                      {item.name}
                    </h3>
                    <p className="mt-1.5 text-[12.5px] leading-relaxed text-white/35">
                      {item.description}
                    </p>
                    <span className="mt-auto pt-5 font-mono text-[12px] uppercase tracking-[0.14em] text-white/20 transition-colors group-hover:text-white/40">
                      Read the guide
                    </span>
                  </SpotlightLink>
                ))}
              </Reveal>
            </div>
          </div>
        </section>

        {/* Docs */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
            <Reveal className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-white/35">
                  Documentation
                </p>
                <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl">
                  Start with a recipe.
                  <br />
                  <span className="text-white/35">Stay for the reference.</span>
                </h2>
              </div>
              <Link
                href="/docs/"
                className="group inline-flex items-center gap-1.5 pb-1 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
              >
                Open the docs
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </Reveal>

            <Reveal className="mt-9 grid gap-3 md:grid-cols-3">
              {resources.map((resource) => (
                <SpotlightLink
                  key={resource.href}
                  href={resource.href}
                  className="min-h-[210px] p-6"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[12px] text-white/25">{resource.index}</span>
                    <ArrowUpRight
                      className="size-4 text-white/20 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-white/60"
                      aria-hidden="true"
                    />
                  </div>
                  <h3 className="mt-8 text-lg font-medium tracking-tight text-white">
                    {resource.title}
                  </h3>
                  <p className="mt-2 text-[12.5px] leading-relaxed text-white/35">
                    {resource.description}
                  </p>
                  <span className="mt-auto pt-5 font-mono text-[12px] uppercase tracking-[0.14em] text-white/20">
                    {resource.tag}
                  </span>
                </SpotlightLink>
              ))}
            </Reveal>
          </div>
        </section>

        {/* FAQ */}
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
            <Reveal>
              <Faq />
            </Reveal>
          </div>
        </section>

        {/* Final CTA */}
        <section className="relative overflow-hidden">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_70%_at_50%_120%,rgba(255,70,85,0.18),transparent_70%)]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 opacity-30 [background-image:linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_70%_80%_at_50%_100%,black,transparent)]"
          />
          <div className="relative mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
            <Reveal className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-white/35">
                  Get started
                </p>
                <h2 className="mt-4 max-w-4xl text-[2.5rem] font-medium leading-[1.02] tracking-[-0.04em] text-white sm:text-5xl lg:text-[4.2rem]">
                  Your next Valorant
                  <br />
                  project{' '}
                  <span className="relative inline-flex items-center border-2 border-white px-3 pb-1 leading-[0.9] sm:px-4">
                    starts here.
                    <span
                      aria-hidden="true"
                      className="absolute -right-1.5 -top-1.5 size-2.5 bg-[#ff4655]"
                    />
                  </span>
                </h2>
              </div>
              <div className="flex flex-wrap items-center gap-2.5 lg:pb-2">
                <Link
                  href="/docs/"
                  className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
                >
                  Read the docs
                  <ArrowUpRight
                    className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                    aria-hidden="true"
                  />
                </Link>
                <Link
                  href="https://github.com/vanshbordia/vlrdevapi"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex h-11 items-center gap-2 border border-white/15 px-5 text-sm font-medium text-white/80 transition-colors hover:border-white/30 hover:bg-white/[0.04] hover:text-white"
                >
                  <GithubIcon className="size-4" />
                  GitHub
                </Link>
              </div>
            </Reveal>

            <div className="mt-12 flex flex-col gap-4 border-t border-white/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
              <CopyCommand command="pip install vlrdevapi" />
              <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                MIT · Python 3.11+ · no API key
              </p>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
