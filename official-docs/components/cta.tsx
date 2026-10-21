import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CopyCommand } from '@/components/landing/copy-command';

interface CtaProps {
  title?: string;
  description?: string;
  docsLabel?: string;
  docsHref?: string;
}

export function CtaSection({
  title = 'Ready to build with VLRdevAPI?',
  description = 'Install the Python SDK and start fetching Valorant esports data in minutes. No API key required.',
  docsLabel = 'Read the docs',
  docsHref = '/docs/',
}: CtaProps) {
  return (
    <section className="mt-16 border border-white/10 bg-[#070707] md:mt-20">
      <div className="relative overflow-hidden p-6 sm:p-8 md:p-10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_55%_70%_at_10%_0%,rgba(255,70,85,0.12),transparent_70%)]"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:radial-gradient(ellipse_80%_100%_at_0%_0%,black,transparent_75%)]"
        />
        <div className="relative">
          <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
            Next step
          </p>
          <h2 className="mt-4 max-w-2xl text-2xl font-medium leading-tight tracking-[-0.03em] text-white md:text-3xl">
            {title}
          </h2>
          <p className="mt-3 max-w-xl text-[14px] leading-relaxed text-white/45">
            {description}
          </p>
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <CopyCommand command="pip install vlrdevapi" />
            <Link
              href={docsHref}
              className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
            >
              {docsLabel}
              <ArrowUpRight
                className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
