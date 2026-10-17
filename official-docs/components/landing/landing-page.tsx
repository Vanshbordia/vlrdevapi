import type { ReactNode } from 'react';
import Link from 'next/link';
import { CopyCommand } from '@/components/ui/copy-command';
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

export interface LandingPageProps {
  /** Route path, for example `/vlr-gg-api`. Used for canonical and breadcrumb URLs. */
  path: string;
  eyebrow: string;
  /** Plain-text H1 for use as the page name in structured data. */
  headline: string;
  h1: ReactNode;
  subtitle: string;
  answer: ReactNode;
  capabilities: LandingCapability[];
  capabilitiesTitle?: string;
  quickstart: { intro: ReactNode; code: string };
  comparison?: LandingComparison;
  faqs: LandingFaq[];
  related: LandingRelated[];
}

export function LandingPage({
  path,
  eyebrow,
  headline,
  h1,
  subtitle,
  answer,
  capabilities,
  capabilitiesTitle = 'What you can fetch',
  quickstart,
  comparison,
  faqs,
  related,
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
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />

      {/* Hero */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 pt-28 pb-14 md:pt-36 md:pb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-fd-primary">{eyebrow}</p>
          <h1 className="mt-4 max-w-3xl font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem]">
            {h1}
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            {subtitle}
          </p>
          <div className="mt-6 max-w-2xl border-l-2 border-fd-primary/40 pl-4">
            <p className="text-base leading-relaxed text-foreground sm:text-lg">{answer}</p>
          </div>
          <div className="mt-7 flex flex-wrap items-center gap-2">
            <CopyCommand command="pip install vlrdevapi" />
            <CopyCommand command="uv add vlrdevapi" />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              href="/docs/"
              className="inline-flex h-11 items-center justify-center bg-foreground px-6 text-sm font-medium tracking-tight text-background transition-all hover:brightness-110 hover:scale-[1.02] active:scale-[0.98]"
            >
              Read the docs
            </Link>
            <Link
              href="/guides/"
              className="inline-flex h-11 items-center justify-center border border-border bg-background/50 px-6 text-sm font-medium tracking-tight text-foreground transition-all hover:bg-muted hover:scale-[1.02] active:scale-[0.98]"
            >
              Tutorial guides
            </Link>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section>
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            {capabilitiesTitle}
          </h2>
          <ul className="mt-8 grid gap-4 sm:grid-cols-2">
            {capabilities.map((capability) => (
              <li key={capability.label} className="border border-border bg-background p-5">
                <h3 className="font-mono text-[0.9375rem] leading-tight text-muted-foreground">
                  {capability.label}
                </h3>
                <p className="mt-3 text-[15px] leading-snug text-muted-foreground sm:text-base">
                  <strong className="font-medium text-foreground">{capability.bold}.</strong>{' '}
                  {capability.text}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Quickstart */}
      <section className="border-t border-border bg-muted/20">
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Quickstart
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">{quickstart.intro}</p>
          <div className="mt-6 max-w-2xl">
            <pre className="overflow-x-auto border border-border bg-background p-4 font-mono text-xs leading-relaxed text-muted-foreground">
              <code>{quickstart.code}</code>
            </pre>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            More detail in the{' '}
            <Link
              href="/docs/quickstart/"
              className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary"
            >
              quickstart docs
            </Link>
            .
          </p>
        </div>
      </section>

      {/* Comparison */}
      {comparison && (
        <section className="border-t border-border">
          <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
            <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
              {comparison.title}
            </h2>
            <div className="mt-6 overflow-x-auto">
              <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-border">
                    {comparison.headers.map((header, i) => (
                      <th
                        key={header || i}
                        scope="col"
                        className={`px-4 py-3 font-semibold ${i === 1 ? 'text-foreground' : 'text-muted-foreground'}`}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparison.rows.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-border">
                      {row.map((cell, cellIndex) => (
                        <td
                          key={cellIndex}
                          className={`px-4 py-3 align-top ${
                            cellIndex === 1
                              ? 'bg-fd-primary/5 font-medium text-foreground'
                              : 'text-muted-foreground'
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
      <section className="border-t border-border">
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Frequently asked questions
          </h2>
          <dl className="mt-8 max-w-3xl divide-y divide-border">
            {faqs.map((faq) => (
              <div key={faq.q} className="py-5 first:pt-0">
                <dt className="text-base font-semibold text-foreground md:text-[1.0625rem]">{faq.q}</dt>
                <dd className="mt-2 text-sm leading-relaxed text-muted-foreground">{faq.a}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-6 text-sm text-muted-foreground">
            More answers in the{' '}
            <Link
              href="/faq/"
              className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary"
            >
              full FAQ
            </Link>
            .
          </p>
        </div>
      </section>

      {/* Related */}
      <section className="border-t border-border">
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Related
          </h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="group flex flex-col border border-border bg-background p-6 transition-all hover:border-fd-primary/50"
              >
                <h3 className="text-base font-bold tracking-tight text-foreground transition-colors group-hover:text-fd-primary">
                  {item.label}
                </h3>
                <p className="mt-2 text-sm leading-snug text-muted-foreground">{item.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
