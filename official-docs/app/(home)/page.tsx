import Link from 'next/link';
import { StickyTabs } from '@/components/home/sticky-tabs';
import { TerminalDemo } from '@/components/home/terminal-demo';
import { CopyCommand } from '@/components/ui/copy-command';
import { HowItWorksCard } from '@/components/home/how-it-works-card';

const jsonLdSoftwareApp = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'VLRdevAPI',
  url: 'https://vlrdevapi.pages.dev',
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg. Fetch match results, player stats, team rosters, and tournament brackets.',
  applicationCategory: 'DeveloperApplication',
  operatingSystem: 'Python 3.11+',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  author: {
    '@type': 'Organization',
    name: 'RiftWatch',
    url: 'https://riftwatch.org',
  },
  downloadUrl: 'https://pypi.org/project/vlrdevapi/',
  sameAs: 'https://github.com/vanshbordia/vlrdevapi',
};

export default function HomePage() {
  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdSoftwareApp).replace(/</g, '\\u003c'),
        }}
      />
      {/* Hero */}
      <section className="relative border-b border-border overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,oklch(0.6677_0.2199_21.34/0.15),transparent)]" />
        <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col justify-start px-6 pt-20 pb-24 md:min-h-screen md:pt-24 md:pb-32 lg:justify-center lg:pt-28 lg:pb-40">
          <div className="grid gap-12 lg:grid-cols-[1fr_1.1fr] lg:items-center lg:gap-16">
            <div className="max-w-2xl">
              <h1 className="font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem] lg:text-[3.5rem] xl:text-[4rem]">
                A Python SDK for{' '}
                <span className="text-fd-primary">Valorant Esports</span>
              </h1>
              <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1.5 text-xs">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                  Python 3.11+
                </span>
                <span className="text-xs text-muted-foreground/40">/</span>
                <Link href="https://pypi.org/project/vlrdevapi/" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 text-xs hover:text-foreground transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 16v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4"/><path d="M8 8h4V4h4v4"/><rect x="2" y="14" width="8" height="6" rx="1"/><rect x="14" y="14" width="8" height="6" rx="1"/></svg>
                  PyPI
                </Link>
              </div>
              <p className="mt-7 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg lg:text-xl">
                A type-safe Python SDK for Valorant esports data from VLR.gg.
                Fetch live match results, player statistics, team rosters, and tournament brackets
                through a fully typed interface. Built by{' '}
                <Link href="https://riftwatch.org" target="_blank" rel="noopener noreferrer" className="text-foreground underline underline-offset-4 decoration-border hover:decoration-foreground/50 transition-colors">RiftWatch</Link>.
              </p>
              <div className="mt-6 flex flex-wrap items-center gap-2">
                <CopyCommand command="pip install vlrdevapi" />
                <CopyCommand command="uv add vlrdevapi" />
              </div>
              <div className="mt-6 flex flex-wrap items-center gap-3">
                <Link
                  href="/docs/"
                  className="inline-flex h-11 items-center justify-center bg-foreground px-6 text-sm font-medium tracking-tight text-background transition-all hover:brightness-110 hover:scale-[1.02] active:scale-[0.98]"
                >
                  Read the Docs
                </Link>
                <Link
                  href="https://github.com/vanshbordia/vlrdevapi"
                  className="inline-flex h-11 items-center justify-center border border-border bg-background/50 px-6 text-sm font-medium tracking-tight text-foreground transition-all hover:bg-muted hover:scale-[1.02] active:scale-[0.98]"
                >
                  View on GitHub
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <TerminalDemo />
            </div>
          </div>
          <div className="mt-10 lg:hidden">
            <TerminalDemo />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="pt-20 md:pt-30 xl:pt-57.25 ">
        <div className="relative mx-auto max-w-7xl px-6 flex flex-col">
          <div className="relative sm:pl-8">
            <div aria-hidden="true" className="absolute -top-20 bottom-0 left-0 z-0 hidden h-[40rem] w-px bg-border sm:block md:-top-30 xl:-top-[14.3125rem]"></div>
            <h2 className="font-heading max-w-[26.5rem] text-[1.75rem] font-bold leading-[1.125] tracking-tight text-foreground md:max-w-[34.375rem] md:text-4xl lg:max-w-[37.25rem] lg:text-[2.5rem] xl:max-w-[39.9375rem] xl:text-[2.75rem] [&_mark]:-ml-1 [&_mark]:inline-flex [&_mark]:h-7 [&_mark]:items-center [&_mark]:bg-fd-primary/20 [&_mark]:box-decoration-clone [&_mark]:pr-0 [&_mark]:pb-2 [&_mark]:pl-1 [&_mark]:text-fd-primary md:[&_mark]:h-8.5 lg:[&_mark]:h-10.5">
              A Python library for Valorant <mark>esports data</mark> from VLR.gg
            </h2>
            <p className="mt-6 max-w-[36rem] text-base leading-relaxed text-muted-foreground lg:mt-7 lg:text-lg">
              Stop scraping VLR.gg by hand. VLRdevAPI handles parsing, data normalization, rate limiting, and type safety so you can build Valorant esports applications faster.
            </p>
          </div>
          <div className="relative z-10 mt-10 sm:mt-14 md:mt-16 xl:mt-20">
            <ul className="flex flex-col items-stretch sm:grid sm:w-full sm:grid-cols-2 [&>li+li]:-mt-px sm:[&>li+li]:mt-0 sm:[&>li:nth-child(2n)]:-ml-px sm:[&>li:nth-child(n+3)]:-mt-px xl:flex xl:flex-row xl:[&>li+li]:-ml-px xl:[&>li]:mt-0">
              {[
                { label: 'Match Data', bold: 'Live scores and stats', text: 'Access live and historical Valorant match results, scores, and statistics from every professional tournaments.' },
                { label: 'Player Stats', bold: 'Performance metrics', text: 'Pull detailed player performance metrics, agent usage data, and career statistics across all major Valorant esports events.' },
                { label: 'Team Info', bold: 'Rosters and rankings', text: 'Get team rosters, rankings, and organization histories for every team competing in the Valorant esports scene worldwide.' },
                { label: 'Event Coverage', bold: 'Tournament data', text: 'Browse tournament brackets, schedule data, and event metadata from VLR.gg - from VCT to regional Valorant circuits.' },
              ].map((f) => (
                <li key={f.label} className="relative flex h-auto flex-col justify-start overflow-hidden border border-border bg-background px-5 pt-5 pb-5 sm:px-6 sm:pt-5 sm:pb-5 xl:px-8 w-full xl:flex-1">
                  <h3 className="font-mono text-[0.9375rem] leading-tight text-muted-foreground">{f.label}</h3>
                  <div className="mt-4 sm:mt-5">
                    <p className="text-[15px] leading-snug text-muted-foreground sm:text-base">
                      <strong className="font-medium text-foreground">{f.bold}.</strong>
                    </p>
                    <p className="mt-1 text-[15px] leading-snug text-muted-foreground sm:text-base">
                      {f.text}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="pt-20 md:pt-30 xl:pt-45 ">
        <div className="mx-auto max-w-7xl px-6">
          <div className="pt-8 md:pt-12 xl:pt-20">
            <div className="inline-flex items-center gap-2.5 rounded border border-border px-3 py-1.5 w-fit">
              <span className="relative h-[0.625rem] w-[0.625rem]">
                <span className="absolute inset-0 rounded-[2px] blur-[5px] bg-fd-primary"></span>
                <span className="absolute inset-0 rounded-[2px] blur-[2px] bg-fd-primary"></span>
                <span className="absolute inset-0 rounded-[2px] bg-fd-primary"></span>
              </span>
              <span className="text-xs font-semibold uppercase tracking-widest text-foreground">How It Works</span>
            </div>
          </div>
          <div className="grid gap-4 pt-[1.25rem] pb-8 sm:gap-5 md:pt-6 md:pb-12 lg:gap-8 xl:grid-cols-[60fr_40fr] xl:pt-[1.75rem] xl:pb-20">
            <h2 className="font-heading text-3xl font-bold leading-[1.125] text-foreground sm:text-[2.5rem] md:max-w-[42rem] md:text-[2.25rem] lg:max-w-[34rem] lg:text-[2.5rem] xl:max-w-none xl:text-[3.25rem]">
              Fetch Valorant esports data in seconds with Python.
            </h2>
            <p className="relative max-w-[26rem] text-base leading-snug tracking-[-0.01em] text-muted-foreground sm:text-lg md:max-w-[31.5rem] md:text-[1.125rem] xl:self-start xl:ml-auto xl:text-xl">
              Install the VLRdevAPI Python package, import the client, and start querying Valorant esports data. Built-in rate limiting and response caching are included out of the box.
            </p>
          </div>
          <div className="-mx-5 z-40 mb-6 self-start bg-background px-5 md:sticky md:top-14 md:-mx-8 md:mb-0 md:px-8 xl:mx-0 xl:px-0">
            <div className="h-[3.75rem] overflow-x-auto border-b border-border [scrollbar-width:none] md:h-16 xl:mx-0 [&::-webkit-scrollbar]:hidden">
              <StickyTabs />
            </div>
          </div>
          <ul className="-mx-5 list-none md:-mx-8 xl:mx-0">
            {[
              { id: 'install', title: 'Install with pip', subtitle: 'One command, zero setup', text: 'Install the VLRdevAPI Python SDK via pip and get started immediately. No complex configuration or system dependencies required.', colors: [[236, 72, 153], [232, 121, 249]] },
              { id: 'import', title: 'Import the library', subtitle: 'Minimal boilerplate', text: 'Import the VLRdevAPI Python client and start fetching Valorant esports data in just two lines of Python code.', colors: [[59, 130, 246], [99, 102, 241]] },
              { id: 'configure', title: 'Set up your client', subtitle: 'Configure once, use everywhere', text: 'Create a VLRdevAPI client instance with your preferred settings. Built-in caching and rate limiting work out of the box.', colors: [[139, 92, 246], [168, 85, 247]] },
              { id: 'fetch', title: 'Query match data', subtitle: 'Live and historical results', text: 'Fetch Valorant match results, player statistics, team rosters, and tournament brackets with fully typed Python responses.', colors: [[16, 185, 129], [5, 150, 105]] },
              { id: 'build', title: 'Build your app', subtitle: 'Typed data, zero guesswork', text: 'Use fully typed Python models to build your Valorant esports application with confidence. Autocomplete and validation in every response.', colors: [[245, 158, 11], [234, 88, 12]] },
            ].map((item, idx) => (
              <li key={item.id}>
                <section id={item.id} className="grid min-h-[24rem] grid-cols-1 sm:min-h-[30rem] lg:min-h-[clamp(33.75rem,41vw,39.25rem)] lg:grid-cols-2" style={{ scrollMarginTop: 128 }}>
                    <div className="flex h-full flex-col justify-center gap-4 sm:gap-8 border border-border px-5 py-6 sm:py-10 md:px-10 md:py-12 lg:border-r-0 lg:px-16 xl:px-24">
                      <div className="text-[1.375rem] leading-[1.125] tracking-[-0.02em] sm:text-[1.625rem] md:text-[1.75rem]">
                        <h3 className="text-foreground">{item.title}</h3>
                        <p className="text-muted-foreground">{item.subtitle}</p>
                      </div>
                      <p className="max-w-md text-[0.9375rem] leading-snug text-muted-foreground sm:text-base">
                        {item.text}
                      </p>
                    </div>
                  <div className="h-full border">
                    <HowItWorksCard
                      colors={item.colors}
                      icon={
                      <div className="flex flex-col gap-3 w-full max-w-sm overflow-x-auto">
                        {item.id === 'install' && (
                          <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                            <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                            <span>pip install vlrdevapi</span>
                          </div>
                        )}
                        {item.id === 'import' && (
                          <>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>from vlrdevapi import VLRdevAPI</span>
                            </div>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>client = VLRdevAPI()</span>
                            </div>
                          </>
                        )}
                        {item.id === 'configure' && (
                          <>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>client = VLRdevAPI(cache_ttl=300)</span>
                            </div>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>client.set_rate_limit(max_per_minute=30)</span>
                            </div>
                          </>
                        )}
                        {item.id === 'fetch' && (
                          <>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>matches = client.get_matches()</span>
                            </div>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>players = client.get_players()</span>
                            </div>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>teams = client.get_teams()</span>
                            </div>
                          </>
                        )}
                        {item.id === 'build' && (
                          <>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>for match in matches:</span>
                            </div>
                            <div className="flex items-center gap-3 rounded border border-border bg-background/80 px-4 py-3 font-mono text-sm text-muted-foreground shadow-sm">
                              <span className="h-2 w-2 rounded-xs bg-fd-primary shrink-0" />
                              <span>&nbsp;&nbsp;&nbsp;&nbsp;print(match.team1, match.score1)</span>
                            </div>
                          </>
                        )}
                      </div>
                      }
                    />
                  </div>
                </section>
                {idx < 4 && (
                  <div className="h-16 md:h-24 border-r border-l border-border" style={{ backgroundImage: 'repeating-linear-gradient(135deg, rgba(128,128,128,0.15) 0px, rgba(128,128,128,0.15) 1px, transparent 1px, transparent 12px)' }} />
                )}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
