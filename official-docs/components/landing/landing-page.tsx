import type { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CodeBlock } from '@/components/landing/code-block';
import { CopyButton } from '@/components/landing/copy-button';
import { CopyCommand } from '@/components/landing/copy-command';
import { JsonLd } from '@/components/json-ld';
import { FaqAccordion } from '@/components/marketing/faq-accordion';
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
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              {eyebrow}
            </p>
            <h2 className="mt-3 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              {title}
            </h2>
            {description ? (
              <p className="mt-4 max-w-xl text-[14px] leading-relaxed text-fd-subtle">
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
  faqIntro = 'Installation, data coverage, and how the SDK behaves under load.',
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
      <section className="relative border-b border-white/10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-fd-primary/70 to-transparent"
        />

        <div className="relative mx-auto grid w-full max-w-7xl gap-12 px-5 pb-14 pt-16 sm:px-8 sm:pb-16 sm:pt-20 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start lg:gap-16 lg:pb-20 lg:pt-24">
          <div className="min-w-0">
            <p className="flex items-center gap-2.5 font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              <span aria-hidden="true" className="size-1.5 bg-fd-primary" />
              {eyebrow}
            </p>

            <h1 className="mt-6 max-w-4xl text-[2.7rem] font-medium leading-[0.98] tracking-[-0.045em] text-white sm:text-[3.6rem] lg:text-[4.2rem]">
              {h1}
            </h1>

            <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-fd-subtle sm:text-base">
              {subtitle}
            </p>

            <p className="mt-5 max-w-2xl text-[14.5px] leading-relaxed text-fd-muted">{answer}</p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/docs/"
                className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
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

            {useCases?.length ? (
              <p className="mt-10 flex flex-wrap items-center gap-x-2 gap-y-1 border-t border-white/10 pt-6 text-[13.5px] leading-relaxed text-fd-subtle">
                <span className="mr-1 font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                  Built for
                </span>
                {useCases.map((item, index) => (
                  <span key={item}>
                    {index > 0 ? (
                      <span aria-hidden="true" className="px-1.5 text-white/20">
                        /
                      </span>
                    ) : null}
                    {item}
                  </span>
                ))}
              </p>
            ) : null}
          </div>

          <aside className="border border-white/10 bg-fd-panel">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-3">
              <span className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                Install
              </span>
              <span aria-hidden="true" className="size-1.5 bg-fd-primary" />
            </div>
            <div className="p-4">
              <div className="space-y-2">
                <CopyCommand command="pip install vlrdevapi" className="w-full" />
                <CopyCommand command="uv add vlrdevapi" className="w-full" />
              </div>
              <dl className="mt-5 space-y-2 border-t border-white/10 pt-4 font-mono text-[12px]">
                {[
                  ['Package', 'vlrdevapi'],
                  ['Python', '3.11+'],
                  ['API key', 'Not required'],
                  ['License', 'MIT'],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between gap-4">
                    <dt className="uppercase tracking-[0.12em] text-fd-muted">{label}</dt>
                    <dd className="text-white/65">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </aside>
        </div>
      </section>

      {/* Capabilities */}
      <section className="border-b border-white/10">
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-4">
            <div>
              <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                Capabilities
              </p>
              <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
                {capabilitiesTitle}
              </h2>
            </div>
          </div>

          <ul className="grid gap-x-10 gap-y-9 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((capability) => (
              <li key={capability.label} className="border-t border-white/10 pt-5">
                <span className="font-mono text-[12px] uppercase tracking-[0.16em] text-fd-muted">
                  {capability.label}
                </span>
                <h3 className="mt-3 text-[15px] font-medium leading-snug tracking-tight text-white/85">
                  {capability.bold}
                </h3>
                <p className="mt-2 text-[13.5px] leading-relaxed text-fd-subtle">
                  {capability.text}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {children}

      {/* Quickstart */}
      <section className="border-b border-white/10 bg-fd-panel">
        <div className="mx-auto grid w-full max-w-7xl gap-10 px-5 py-14 sm:px-8 sm:py-16 lg:grid-cols-[0.8fr_1.2fr] lg:items-start lg:gap-16">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              Quickstart
            </p>
            <h2 className="mt-3 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              {quickstart.title ?? 'From install to data in one file.'}
            </h2>
            <p className="mt-4 max-w-xl text-[14px] leading-relaxed text-fd-subtle">
              {quickstart.intro}
            </p>
            <ol className="mt-7 space-y-4">
              {(quickstart.steps ?? defaultQuickstartSteps).map((step, index) => (
                <li key={step.title} className="flex items-start gap-3">
                  <span className="mt-0.5 font-mono text-[12px] text-fd-primary">
                    0{index + 1}
                  </span>
                  <span className="min-w-0">
                    <span className="block text-[13px] font-medium text-white/70">
                      {step.title}
                    </span>
                    <span className="mt-0.5 block text-[12.5px] leading-relaxed text-fd-muted">
                      {step.text}
                    </span>
                  </span>
                </li>
              ))}
            </ol>
            <Link
              href="/docs/quickstart/"
              className="group mt-7 inline-flex items-center gap-1.5 text-[13px] font-medium text-white/60 transition-colors hover:text-white"
            >
              Full quickstart
              <ArrowUpRight
                className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>

          <div className="overflow-hidden border border-white/10 bg-fd-canvas">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-3">
              <div className="flex items-center gap-2">
                <span aria-hidden="true" className="size-1.5 bg-fd-primary" />
                <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
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
                  <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                    {quickstart.outputLabel ?? 'Output'}
                  </span>
                  <span className="font-mono text-[12px] text-fd-primary">typed result</span>
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
                <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
                  Compare
                </p>
                <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
                  {comparison.title}
                </h2>
              </div>
            </div>
            <div className="mt-8 overflow-x-auto border border-white/10 bg-fd-panel">
              <table className="w-full min-w-[46rem] border-collapse text-left text-[13px]">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.02]">
                    {comparison.headers.map((header, index) => (
                      <th
                        key={header || index}
                        scope="col"
                        className={`px-4 py-3 font-mono text-[12px] font-normal uppercase tracking-[0.12em] ${
                          index === 1 ? 'text-fd-primary' : 'text-fd-muted'
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
                      {row.map((cell, cellIndex) =>
                        cellIndex === 0 ? (
                          <th
                            key={cellIndex}
                            scope="row"
                            className="px-4 py-3 text-left align-top font-mono text-[12px] font-normal uppercase tracking-[0.1em] text-fd-muted"
                          >
                            {cell}
                          </th>
                        ) : (
                          <td
                            key={cellIndex}
                            className={`px-4 py-3 align-top ${
                              cellIndex === 1
                                ? 'border-l border-fd-primary/20 bg-fd-primary/[0.04] text-white/85'
                                : 'text-white/55'
                            }`}
                          >
                            {cell}
                          </td>
                        ),
                      )}
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
            <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              FAQ
            </p>
            <h2 className="mt-2 text-2xl font-medium tracking-[-0.03em] text-white sm:text-3xl">
              Frequently asked questions
            </h2>
            <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-fd-muted">
              {faqIntro}
            </p>
            <Link
              href="/faq/"
              className="group mt-6 inline-flex items-center gap-1.5 text-[13px] font-medium text-white/60 transition-colors hover:text-white"
            >
              Full FAQ
              <ArrowUpRight
                className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          </div>

          <FaqAccordion
            items={faqs.map((faq) => ({ q: faq.q, a: faq.a }))}
            questionClassName="max-w-2xl text-[15px] font-medium leading-relaxed text-white/85 transition-colors group-hover:text-white"
            answerClassName="max-w-2xl pb-5 pr-10 text-[14px] leading-relaxed text-white/55"
          />
        </div>
      </section>

      {/* Related */}
      <section className="border-b border-white/10">
        <div className="mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="flex items-center gap-4">
            <h2 className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
              Related
            </h2>
            <span aria-hidden="true" className="h-px flex-1 bg-white/10" />
          </div>
          <ul className="mt-6 grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((item) => (
              <li key={item.href} className="border-t border-white/10 pt-5">
                <Link
                  href={item.href}
                  className="group flex items-center justify-between gap-4 text-[15px] font-medium tracking-tight text-white/85 transition-colors hover:text-white"
                >
                  <span>{item.label}</span>
                  <ArrowUpRight
                    className="size-3.5 shrink-0 text-white/20 transition-all duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-fd-primary"
                    aria-hidden="true"
                  />
                </Link>
                <p className="mt-2 text-[13px] leading-relaxed text-fd-muted">{item.desc}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-fd-panel">
        <div className="relative mx-auto w-full max-w-7xl px-5 py-14 sm:px-8 sm:py-16">
          <div className="relative flex flex-col gap-7 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-fd-muted">
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
                className="group inline-flex h-11 items-center gap-1.5 border border-white bg-white px-5 text-[13px] font-medium text-black transition-colors hover:border-fd-primary hover:bg-fd-primary hover:text-white"
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
