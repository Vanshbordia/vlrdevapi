import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CopyCommand } from '@/components/landing/copy-command';
import { GithubIcon } from '@/components/landing/github-icon';
import { Reveal } from '@/components/landing/reveal';
import { project } from '@/lib/project';

/** Closing call to action. */
export function FinalCta() {
  return (
    <section className="bg-fd-panel">
      <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:py-28">
        <Reveal className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">Get started</p>
            <h2 className="mt-4 max-w-3xl text-[2.5rem] font-medium leading-[1.02] tracking-[-0.04em] text-white sm:text-5xl lg:text-[3.6rem]">
              Install the SDK and query the data.
            </h2>
            <p className="mt-5 max-w-xl text-[14.5px] leading-relaxed text-fd-subtle">
              One package, six namespaces, no key. Start with the quickstart, then dig into the
              endpoint reference.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2.5 lg:pb-2">
            <Link
              href="/docs/"
              className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-6 text-sm font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
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
          <CopyCommand />
          <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
            MIT · Python 3.11+ · v{project.version} · no API key
          </p>
        </div>
      </div>
    </section>
  );
}
