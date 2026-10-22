import { Clock3, Gauge, Layers, Workflow } from 'lucide-react';
import { ParallelDemo, TimezoneDemo, TypedFieldsDemo } from '@/components/landing/bento-demos';
import { CurriedDemo } from '@/components/landing/curried-demo';
import { RateLimitDemo } from '@/components/landing/rate-limit-demo';
import { Reveal } from '@/components/landing/reveal';
import { SpotlightCard } from '@/components/landing/spotlight-card';

/** What the library takes care of for you. */
export function Features() {
  return (
    <section className="border-b border-white/10">
      <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
        <Reveal className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">
              What it handles
            </p>
            <h2 className="mt-4 max-w-2xl text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl lg:text-[2.9rem]">
              The parts you would
              <br />
              <span className="text-fd-muted">otherwise have to write.</span>
            </h2>
          </div>
          <p className="max-w-md text-[14.5px] leading-relaxed text-fd-subtle lg:justify-self-end lg:pb-1">
            No HTML parsing. No selectors that break when VLR.gg ships a redesign. No glue code
            between the site and your app — just import the client and query the data.
          </p>
        </Reveal>

        <div className="mt-12 grid gap-3 lg:grid-cols-12">
          <Reveal className="lg:col-span-7">
            <SpotlightCard className="h-full p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Typed models
                  </p>
                  <h3 className="mt-3 text-lg font-medium tracking-tight text-white sm:text-xl">
                    No more dict.get(&quot;name&quot;)
                  </h3>
                  <p className="mt-2 max-w-md text-[13px] leading-relaxed text-fd-subtle">
                    Every response is a Pydantic model with real fields, types, and descriptions.
                    Autocomplete works. Validation is free.
                  </p>
                </div>
                <Layers className="size-5 shrink-0 text-fd-muted" aria-hidden="true" />
              </div>
              <TypedFieldsDemo />
            </SpotlightCard>
          </Reveal>

          <Reveal delay={70} className="lg:col-span-5">
            <SpotlightCard className="h-full p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Curried access
                  </p>
                  <h3 className="mt-3 text-lg font-medium tracking-tight text-white sm:text-xl">
                    Bind once, query anywhere
                  </h3>
                  <p className="mt-2 text-[13px] leading-relaxed text-fd-subtle">
                    Pass an ID one time. Every related method hangs off the object you get back.
                  </p>
                </div>
              </div>
              <CurriedDemo />
            </SpotlightCard>
          </Reveal>

          <Reveal className="lg:col-span-4">
            <SpotlightCard className="h-full p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Rate limiting
                  </p>
                  <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                    A good citizen by default
                  </h3>
                </div>
                <Gauge className="size-5 shrink-0 text-fd-muted" aria-hidden="true" />
              </div>
              <p className="mt-2 text-[12.5px] leading-relaxed text-fd-subtle">
                Three requests per second out of the box, with retries and exponential backoff.
              </p>
              <RateLimitDemo />
            </SpotlightCard>
          </Reveal>

          <Reveal delay={60} className="lg:col-span-4">
            <SpotlightCard className="h-full p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Concurrency
                  </p>
                  <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                    Parallel where it counts
                  </h3>
                </div>
                <Workflow className="size-5 shrink-0 text-fd-muted" aria-hidden="true" />
              </div>
              <p className="mt-2 text-[12.5px] leading-relaxed text-fd-subtle">
                Multi-stage endpoints fetch their pages in parallel with a thread pool.
              </p>
              <ParallelDemo />
            </SpotlightCard>
          </Reveal>

          <Reveal delay={120} className="lg:col-span-4">
            <SpotlightCard className="h-full p-6 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                    Timezones
                  </p>
                  <h3 className="mt-3 text-[15px] font-medium tracking-tight text-white">
                    Timezones, handled
                  </h3>
                </div>
                <Clock3 className="size-5 shrink-0 text-fd-muted" aria-hidden="true" />
              </div>
              <p className="mt-2 text-[12.5px] leading-relaxed text-fd-subtle">
                VLR.gg renders times for a viewer. Set source_tz once and dates come back UTC-aware.
              </p>
              <TimezoneDemo />
            </SpotlightCard>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
