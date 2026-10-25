import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CopyCommand } from '@/components/landing/copy-command';
import { HeroDemo } from '@/components/landing/hero-demo';
import { Reveal } from '@/components/landing/reveal';
import { project } from '@/lib/project';

/**
 * Landing hero.
 *
 * A Server Component: only the interactive demo and the copy button are
 * client islands.
 */
export function Hero() {
  return (
    <section className="relative border-b border-white/10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-fd-primary/70 to-transparent"
      />

      {/* A single soft bloom, pushed slightly in from the top-right corner. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_58%_52%_at_72%_-4%,rgba(255,70,85,0.18),rgba(255,70,85,0.06)_45%,transparent_72%)]"
      />

      <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-16 sm:px-8 sm:pb-20 sm:pt-20 lg:pb-24 lg:pt-28">
        <div className="grid gap-12 lg:grid-cols-[1.02fr_0.98fr] lg:items-start lg:gap-14 xl:gap-20">
          <div>
            <Reveal>
              <div className="flex flex-wrap items-center gap-3">
                <p className="flex items-center gap-2.5 font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                  <span aria-hidden="true" className="size-1.5 bg-fd-primary" />
                  Python SDK &amp; MCP for VLR.gg
                </p>
                <Link
                  href="/changelog/"
                  className="group inline-flex items-center gap-1.5 border border-white/15 bg-white/[0.03] px-2 py-0.5 font-mono text-[11px] text-white/70 transition-colors hover:border-fd-primary/50 hover:text-white"
                >
                  <span>v{project.version} released</span>
                  <ArrowUpRight className="size-3 text-fd-primary transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                </Link>
              </div>
            </Reveal>

            <h1 className="mt-7 text-[2.3rem] font-medium leading-[1.02] tracking-[-0.04em] text-white sm:text-[3.3rem] lg:text-[3.8rem] xl:text-[4.2rem]">
              <span className="landing-enter block" style={{ animationDelay: '40ms' }}>
                Valorant esports
              </span>
              <span className="landing-enter block" style={{ animationDelay: '120ms' }}>
                data, straight
              </span>
              <span className="landing-enter block" style={{ animationDelay: '200ms' }}>
                into <span className="text-fd-primary">Python.</span>
              </span>
            </h1>

            <Reveal delay={140}>
              <p className="mt-7 max-w-lg text-[15px] leading-relaxed text-fd-subtle sm:text-base">
                VLRdevAPI reads VLR.gg and returns Pydantic models for matches, players, teams,
                events, and series. No API key, no account, and no parser to maintain.
              </p>
            </Reveal>

            <Reveal
              delay={210}
              className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center"
            >
              <Link
                href="/docs/"
                className="group inline-flex h-11 items-center justify-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
              >
                Read the docs
                <ArrowUpRight
                  className="size-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <CopyCommand />
            </Reveal>

            <Reveal delay={260}>
              <p className="mt-10 flex items-center gap-2.5 border-t border-white/10 pt-6 text-[13px] text-fd-muted">
                <span aria-hidden="true" className="size-1.5 shrink-0 bg-fd-primary" />
                Used by partnered, Tier 1, Tier 2, and Game Changers orgs.
              </p>
            </Reveal>
          </div>

          <Reveal delay={160} className="relative min-w-0">
            <HeroDemo />
          </Reveal>
        </div>
      </div>
    </section>
  );
}
