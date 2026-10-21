import type { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowUpRight, ChevronDown } from 'lucide-react';
import { CodeBlock } from '@/components/landing/code-block';
import { CopyButton } from '@/components/landing/copy-button';
import { CopyCommand } from '@/components/landing/copy-command';
import { JsonLd } from '@/components/json-ld';
import { canonicalUrl, siteUrl } from '@/lib/shared';
import { projectAuthor } from '@/lib/project';

export interface LandingFaq {
  q: string;
  a: string;
}

export interface LandingCapability {
  label: string;
  bold: string;
  text: string;
}

export interface LandingRelated {
  href: string;
  label: string;
  desc: string;
}

export interface LandingComparison {
  title: string;
  headers: string[];
  rows: string[][];
}

export interface LandingQuickstart {
  intro: ReactNode;
  code: string;
  title?: string;
  file?: string;
  output?: string;
  outputLabel?: string;
  steps?: Array<{ title: string; text: string }>;
}

export interface LandingPageProps {
  /** Route path, for example `/vlr-gg-api`. Used for canonical and breadcrumb URLs. */
  path: string;
  eyebrow: string;
  /** Plain-text H1 for use as the page name in structured data. */
  headline: string;
  h1: ReactNode;
  subtitle: string;
  answer: ReactNode;
  useCases?: string[];
  capabilities: LandingCapability[];
  capabilitiesTitle?: string;
  quickstart: LandingQuickstart;
  comparison?: LandingComparison;
  faqs: LandingFaq[];
  faqIntro?: string;
  related: LandingRelated[];
  children?: ReactNode;
}

const defaultQuickstartSteps = [
  {
    title: 'Install the package from PyPI.',
    text: 'No API key and no separate service to configure.',
  },
  {
    title: 'Call a namespace and fetch data.',
    text: 'Each method returns a typed response instead of raw HTML.',
  },
  {
    title: 'Use the models in your app.',
    text: 'Autocomplete, validation, and serialization are included.',
  },
];

export function LandingSection({
  eyebrow,
  title,
  description,
  action,
  children,
}: {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="border-b border-white/10">
      <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-2xl">
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
              {eyebrow}
            </p>
            <h2 className="mt-3 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              {title}
            </h2>
            {description ? (
              <p className="mt-4 max-w-xl text-[14px] leading-relaxed text-white/45">
                {description}
              </p>
            ) : null}
          </div>
          {action}
        </div>
        <div className="mt-8">{children}</div>
      </div>
    </section>
  );
}

export function LandingPage({
  path,
  eyebrow,
  headline,
  h1,
  subtitle,
  answer,
  useCases,
  capabilities,
  capabilitiesTitle = 'What you can fetch',
  quickstart,
  comparison,
  faqs,
  faqIntro = 'Short answers about installation, data coverage, and how the SDK works.',
  related,
  children,
}: LandingPageProps) {
  const url = canonicalUrl(path);

  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      '@id': `${url}#webpage`,
      url,
      name: headline,
      description: subtitle,
      inLanguage: 'en',
      isPartOf: { '@id': `${siteUrl}/#website` },
      about: { '@id': `${siteUrl}/#software` },
      author: projectAuthor,
      publisher: { '@id': `${siteUrl}/#organization` },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqs.map((faq) => ({
        '@type': 'Question',
        name: faq.q,
        acceptedAnswer: { '@type': 'Answer', text: faq.a },
      })),
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: canonicalUrl('/') },
        { '@type': 'ListItem', position: 2, name: headline, item: url },
      ],
    },
  ];

  return (
    <main id="main" tabIndex={-1} className="flex-1">
      <JsonLd data={jsonLd} />

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-white/10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_58%_58%_at_80%_-12%,rgba(255,70,85,0.14),transparent_72%)]"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 opacity-50 [background-image:linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] [background-size:84px_84px] [mask-image:radial-gradient(ellipse_85%_65%_at_50%_0%,black,transparent_78%)]"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-0 h-px w-[min(92vw,72rem)] -translate-x-1/2 bg-gradient-to-r from-transparent via-[#ff4655]/60 to-transparent"
        />

        <div className="relative mx-auto grid w-full max-w-7xl gap-12 px-5 pb-14 pt-14 sm:px-8 sm:pb-16 sm:pt-20 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-end lg:gap-16 lg:pb-20 lg:pt-24">
          <div className="min-w-0">
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-[#ff8d97]">
              {eyebrow}
            </p>
            <h1 className="mt-5 max-w-4xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.8rem] lg:text-[4.4rem]">
              {h1}
            </h1>
            <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-white/50 sm:text-base">
              {subtitle}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/docs/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
              >
                Read the docs
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <Link
                href="/guides/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white/15 px-5 text-[13px] font-medium text-white/65 transition-colors hover:border-white/30 hover:text-white"
              >
                Tutorial guides
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </div>
          </div>

          <aside className="border border-white/10 bg-[#070707]">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-3">
              <span className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/35">
                Install
              </span>
              <span aria-hidden="true" className="size-1.5 bg-[#ff4655]" />
            </div>
            <div className="p-4">
              <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
                Terminal
              </p>
              <div className="mt-3 space-y-2">
                <CopyCommand command="pip install vlrdevapi" className="w-full justify-between" />
                <CopyCommand command="uv add vlrdevapi" className="w-full justify-between" />
              </div>
              <dl className="mt-5 space-y-2 border-t border-white/10 pt-4 font-mono text-[12px]">
                {[
                  ['Package', 'vlrdevapi'],
                  ['Python', '3.11+'],
                  ['API key', 'Not required'],
                  ['License', 'MIT'],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between gap-4">
                    <dt className="uppercase tracking-[0.12em] text-white/25">{label}</dt>
                    <dd className="text-white/60">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </aside>
        </div>

        <div className="relative mx-auto w-full max-w-7xl px-5 pb-14 sm:px-8">
          <div className="max-w-5xl border-l-2 border-[#ff4655] bg-white/[0.02] p-5 md:p-6">
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
              Short answer
            </p>
            <p className="mt-3 max-w-4xl text-[15px] leading-relaxed text-white/65">{answer}</p>
          </div>
        </div>
      </section>

      {useCases?.length ? (
        <section
          aria-label="What this page is built for"
          className="border-b border-white/10 bg-white/[0.01]"
        >
          <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center gap-x-5 gap-y-2 px-5 py-4 sm:px-8">
            <span className="shrink-0 font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
              Built for
            </span>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
              {useCases.map((item, index) => (
                <span
                  key={item}
                  className="flex items-center gap-4 text-[13px] font-medium tracking-[-0.01em] text-white/40"
                >
                  {index > 0 ? (
                    <span aria-hidden="true" className="font-mono text-[12px] text-[#ff4655]/60">
                      /
                    </span>
                  ) : null}
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {/* Capabilities */}
      <section className="border-b border-white/10">
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-4">
            <div>
              <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
                Capabilities
              </p>
              <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
                {capabilitiesTitle}
              </h2>
            </div>
            <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
              {String(capabilities.length).padStart(2, '0')} modules
            </span>
          </div>

          <ul className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((capability, index) => (
              <li
                key={capability.label}
                className="group relative overflow-hidden border border-white/10 bg-[#070707] p-5 transition-colors hover:border-[#ff4655]/40"
              >
                <span
                  aria-hidden="true"
                  className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-[#ff4655] transition-transform duration-300 group-hover:scale-x-100"
                />
                <div className="flex items-center justify-between gap-4">
                  <span className="font-mono text-[12px] text-[#ff4655]">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="font-mono text-[12px] uppercase tracking-[0.12em] text-white/25">
                    {capability.label}
                  </span>
                </div>
                <h3 className="mt-6 text-lg font-medium leading-snug tracking-tight text-white/85">
                  {capability.bold}
                </h3>
                <p className="mt-3 text-[13.5px] leading-relaxed text-white/40">
                  {capability.text}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {children}

      {/* Quickstart */}
      <section className="border-b border-white/10 bg-[#050505]">
        <div className="mx-auto grid w-full max-w-7xl gap-10 px-5 py-14 sm:px-8 sm:py-16 lg:grid-cols-[0.8fr_1.2fr] lg:items-start lg:gap-16">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
              Quickstart
            </p>
            <h2 className="mt-3 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              {quickstart.title ?? 'From install to data in one file.'}
            </h2>
            <p className="mt-4 max-w-xl text-[14px] leading-relaxed text-white/45">
              {quickstart.intro}
            </p>
            <ol className="mt-7 space-y-4">
              {(quickstart.steps ?? defaultQuickstartSteps).map((step, index) => (
                <li key={step.title} className="flex items-start gap-3">
                  <span className="mt-0.5 font-mono text-[12px] text-[#ff4655]">
                    0{index + 1}
                  </span>
                  <span className="min-w-0">
                    <span className="block text-[13px] font-medium text-white/60">
                      {step.title}
                    </span>
                    <span className="mt-0.5 block text-[12.5px] leading-relaxed text-white/35">
                      {step.text}
                    </span>
                  </span>
                </li>
              ))}
            </ol>
            <Link
              href="/docs/quickstart/"
              className="group mt-7 inline-flex items-center gap-1.5 text-[13px] font-medium text-white/55 transition-colors hover:text-white"
            >
              Full quickstart
              <ArrowUpRight
                className="size-3.5 text-[#ff8d97] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>

          <div className="overflow-hidden border border-white/10 bg-[#070707]">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-3">
              <div className="flex items-center gap-2">
                <span aria-hidden="true" className="size-1.5 bg-[#ff4655]" />
                <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/35">
                  {quickstart.file ?? 'example.py'}
                </span>
              </div>
              <CopyButton
                value={quickstart.code}
                label="Copy example code"
                className="border-white/10 bg-transparent"
              />
            </div>
            <CodeBlock code={quickstart.code} />
            {quickstart.output ? (
              <div className="border-t border-white/10">
                <div className="flex items-center justify-between gap-4 px-4 py-2.5">
                  <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/30">
                    {quickstart.outputLabel ?? 'Output'}
                  </span>
                  <span className="font-mono text-[12px] text-[#ff8d97]">typed result</span>
                </div>
                <CodeBlock code={quickstart.output} lineNumbers={false} />
              </div>
            ) : null}
          </div>
        </div>
      </section>

      {/* Comparison */}
      {comparison && (
        <section className="border-b border-white/10">
          <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
            <div className="flex items-end justify-between gap-4 border-b border-white/10 pb-4">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
                  Compare
                </p>
                <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
                  {comparison.title}
                </h2>
              </div>
            </div>
            <div className="mt-8 overflow-x-auto border border-white/10 bg-[#070707]">
              <table className="w-full min-w-[46rem] border-collapse text-left text-[13px]">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.02]">
                    {comparison.headers.map((header, index) => (
                      <th
                        key={header || index}
                        scope="col"
                        className={`px-4 py-3 font-mono text-[12px] font-normal uppercase tracking-[0.12em] ${
                          index === 1 ? 'text-[#ff8d97]' : 'text-white/30'
                        }`}
                      >
                        {header || <span className="sr-only">Feature</span>}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparison.rows.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-white/10 last:border-b-0">
                      {row.map((cell, cellIndex) => (
                        <td
                          key={cellIndex}
                          className={`px-4 py-3 align-top ${
                            cellIndex === 0
                              ? 'font-mono text-[12px] uppercase tracking-[0.1em] text-white/25'
                              : cellIndex === 1
                                ? 'border-l border-[#ff4655]/20 bg-[#ff4655]/[0.04] text-white/75'
                                : 'text-white/40'
                          }`}
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}

      {/* FAQ */}
      <section className="border-b border-white/10">
        <div className="mx-auto grid w-full max-w-7xl gap-10 px-5 py-14 sm:px-8 sm:py-16 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
              FAQ
            </p>
            <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              Frequently asked questions
            </h2>
            <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-white/40">
              {faqIntro}
            </p>
            <Link
              href="/faq/"
              className="group mt-6 inline-flex items-center gap-1.5 text-[13px] font-medium text-white/55 transition-colors hover:text-white"
            >
              Full FAQ
              <ArrowUpRight
                className="size-3.5 text-[#ff8d97] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>

          <div className="border-t border-white/10">
            {faqs.map((faq) => (
              <details key={faq.q} className="group border-b border-white/10">
                <summary className="flex cursor-pointer list-none items-start justify-between gap-6 py-5 text-[15px] font-medium leading-relaxed text-white/75 transition-colors hover:text-white [&::-webkit-details-marker]:hidden">
                  <span className="max-w-2xl">{faq.q}</span>
                  <span
                    aria-hidden="true"
                    className="mt-0.5 flex size-7 shrink-0 items-center justify-center border border-white/10 text-white/30 transition-colors group-open:border-[#ff4655]/40 group-open:bg-[#ff4655]/10 group-open:text-[#ff8d97]"
                  >
                    <ChevronDown className="size-3.5 transition-transform duration-200 group-open:rotate-180" />
                  </span>
                </summary>
                <p className="max-w-2xl pb-5 pr-10 text-[14px] leading-relaxed text-white/45">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Related */}
      <section className="border-b border-white/10">
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="flex items-center gap-4">
            <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-white/30">
              Related
            </h2>
            <span aria-hidden="true" className="h-px flex-1 bg-white/10" />
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="group relative flex flex-col overflow-hidden border border-white/10 bg-[#070707] p-5 transition-colors hover:border-[#ff4655]/40"
              >
                <span
                  aria-hidden="true"
                  className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-[#ff4655] transition-transform duration-300 group-hover:scale-x-100"
                />
                <div className="flex items-start justify-between gap-4">
                  <h3 className="text-[15px] font-medium tracking-tight text-white/80 transition-colors group-hover:text-white">
                    {item.label}
                  </h3>
                  <ArrowUpRight
                    className="mt-0.5 size-3.5 shrink-0 text-white/20 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[#ff8d97]"
                    aria-hidden="true"
                  />
                </div>
                <p className="mt-2 text-[13px] leading-relaxed text-white/40">{item.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-[#050505]">
        <div className="relative mx-auto w-full max-w-7xl overflow-hidden px-5 py-14 sm:px-8 sm:py-16">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_45%_100%_at_12%_0%,rgba(255,70,85,0.12),transparent_72%)]"
          />
          <div className="relative flex flex-col gap-7 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-[#ff8d97]">
                Start building
              </p>
              <h2 className="mt-3 max-w-2xl text-3xl font-medium leading-tight tracking-[-0.03em] text-white sm:text-4xl">
                Install the SDK and query the data.
              </h2>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <CopyCommand command="pip install vlrdevapi" />
              <Link
                href="/docs/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-[#ff4655] hover:bg-[#ff4655] hover:text-white"
              >
                Read the docs
                <ArrowUpRight
                  className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
