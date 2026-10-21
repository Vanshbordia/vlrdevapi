import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { LandingPage, LandingSection } from '@/components/landing/landing-page';
import { createPageMetadata } from '@/lib/seo';

export const metadata: Metadata = createPageMetadata({
  title: 'VLR.gg API for Python (Unofficial)',
  description:
    'VLR.gg has no public API. VLRdevAPI is a free, typed Python client that fetches matches, players, teams, events, and news from VLR.gg with no API key.',
  path: '/vlr-gg-api/',
});

const pipeline = [
  {
    label: '01 / Request',
    title: 'Fetch the page',
    text: 'The client requests the same public VLR.gg page you would open in a browser.',
    detail: 'vlrdevapi.matches.upcoming()',
  },
  {
    label: '02 / Parse',
    title: 'Extract the data',
    text: 'A maintained parser turns the markup into models, including nested teams and events.',
    detail: 'UpcomingMatchesPage',
  },
  {
    label: '03 / Return',
    title: 'Hand back types',
    text: 'Your app receives fields, lists, and nested objects instead of an HTML document.',
    detail: 'match.team1.name',
  },
];

const returnedFields = [
  ['match.match_id', 'int'],
  ['match.event', 'str'],
  ['match.stage', 'str'],
  ['match.team1.name', 'str | None'],
  ['match.datetime', 'datetime | None'],
  ['match.eta', 'str'],
];

export default function VlrGgApiPage() {
  return (
    <LandingPage
      path="/vlr-gg-api"
      eyebrow="VLR.gg API"
      headline="VLR.gg API for Python"
      h1={
        <>
          The VLR.gg API for <span className="text-[#ff4655]">Python</span>
        </>
      }
      subtitle="VLR.gg does not publish a public API. VLRdevAPI is a free, open-source Python client that reads VLR.gg for you and returns typed objects, so you can query Valorant esports data without writing or maintaining a scraper."
      answer="Short answer: VLR.gg has no official API. VLRdevAPI is an unofficial Python client that fetches and parses VLR.gg pages, then returns Pydantic models. It needs no API key and runs on Python 3.11 or newer."
      useCases={[
        'Match pages',
        'Roster trackers',
        'Tournament calendars',
        'News readers',
        'Discord bots',
        'Scouting tools',
      ]}
      capabilitiesTitle="What you can pull from VLR.gg"
      capabilities={[
        {
          label: 'Matches',
          bold: 'Upcoming, live, and completed results',
          text: 'Scores, scoreboards, and match metadata from VCT and regional Valorant events.',
        },
        {
          label: 'Players',
          bold: 'Profiles and statistics',
          text: 'Agent usage, match history, and career statistics for professional Valorant players.',
        },
        {
          label: 'Teams',
          bold: 'Rosters and rankings',
          text: 'Team info, current rosters, placements, and match history.',
        },
        {
          label: 'Events',
          bold: 'Tournaments and standings',
          text: 'Event listings, stages, participating teams, and group standings.',
        },
        {
          label: 'Series',
          bold: 'VODs and round data',
          text: 'Series info, VOD links, round-by-round data, and player economy statistics.',
        },
        {
          label: 'News',
          bold: 'Articles and listings',
          text: 'The VLR.gg news feed and full articles returned as Markdown.',
        },
      ]}
      quickstart={{
        title: 'Ask for the next matches.',
        file: 'upcoming.py',
        intro:
          'Fetch the upcoming match list and read teams, event, stage, ETA, and start time as typed fields. No selectors and no HTML leaves the client.',
        steps: [
          {
            title: 'Install the client.',
            text: 'pip install vlrdevapi. No key, account, or separate service.',
          },
          {
            title: 'Request the page.',
            text: 'matches.upcoming() returns the next page of scheduled matches.',
          },
          {
            title: 'Read the models.',
            text: 'Teams, event, stage, ETA, and the UTC datetime are already parsed.',
          },
        ],
        code: `import vlrdevapi

page = vlrdevapi.matches.upcoming()

for match in page.matches[:3]:
    team1 = match.team1.name if match.team1 else "TBD"
    team2 = match.team2.name if match.team2 else "TBD"
    print(f"{team1} vs {team2}")
    print(f"  {match.event} · {match.stage} · {match.eta}")`,
        outputLabel: 'Example output',
        output: `NRG vs FNATIC
  VCT 2026: EMEA Stage 1 · Playoffs · 2h 14m
Team Heretics vs Team Vitality
  VCT 2026: EMEA Stage 1 · Playoffs · 4h 02m
FUT Esports vs Karmine Corp
  VCT 2026: EMEA Stage 1 · Group Stage · 1d 3h`,
      }}
      comparison={{
        title: 'How do you get VLR.gg data in Python?',
        headers: ['', 'VLRdevAPI', 'Scraping VLR.gg', 'Riot official API'],
        rows: [
          ['Setup', 'pip install vlrdevapi', 'Write and maintain parsers', 'Register an app and key'],
          ['Data source', 'VLR.gg esports pages', 'VLR.gg esports pages', 'Riot account and match endpoints'],
          ['Output', 'Typed Pydantic models', 'Raw HTML', 'Riot JSON'],
          ['Rate limiting', 'Built in', 'Your responsibility', 'Per-key limits'],
          ['Cost', 'Free', 'Free', 'Free tier with limits'],
          ['API key', 'Not required', 'Not required', 'Required'],
        ],
      }}
      faqs={[
        {
          q: 'Does VLR.gg have an API?',
          a: 'No. VLR.gg does not publish a public API. VLRdevAPI is an unofficial client that fetches and parses VLR.gg pages on your behalf.',
        },
        {
          q: 'Is VLRdevAPI free?',
          a: 'Yes. VLRdevAPI is free and open source under the MIT license. It does not require an API key, a subscription, or an account.',
        },
        {
          q: 'Is this an official VLR.gg or Riot product?',
          a: 'No. VLRdevAPI is an independent open-source project. It is not affiliated with, endorsed by, or connected to VLR.gg or Riot Games.',
        },
        {
          q: 'What can I fetch from VLR.gg?',
          a: 'Upcoming, live, and completed matches; player profiles and statistics; team rosters and rankings; events, stages, and standings; series, VODs, and round data; and the news feed.',
        },
        {
          q: 'Which Python versions are supported?',
          a: 'Python 3.11 and newer.',
        },
        {
          q: 'How fast can I request data?',
          a: 'The client applies a built-in rate limit and caches responses. Multi-stage endpoints also fetch their pages in parallel.',
        },
      ]}
      faqIntro="Straight answers about VLR.gg coverage, the unofficial status, rate limits, and what the client actually returns."
      related={[
        {
          href: '/valorant-esports-api/',
          label: 'Valorant esports API',
          desc: 'A wider look at the esports data VLRdevAPI exposes in Python.',
        },
        {
          href: '/docs/getting-started/',
          label: 'Getting started',
          desc: 'Install the SDK and make your first request.',
        },
        {
          href: '/docs/reference/',
          label: 'API reference',
          desc: 'Every namespace, method, and model in the library.',
        },
        {
          href: '/guides/',
          label: 'Tutorial guides',
          desc: 'Build a match monitor, a stats dashboard, and more.',
        },
        {
          href: '/blog/vlrdevapi-vs-web-scraping/',
          label: 'VLRdevAPI vs web scraping',
          desc: 'How the SDK compares to parsing VLR.gg yourself.',
        },
        {
          href: '/faq/',
          label: 'FAQ',
          desc: 'Answers about rate limits, caching, and data coverage.',
        },
      ]}
    >
      <LandingSection
        eyebrow="Under the hood"
        title="VLR.gg has no public API. This is the layer that acts like one."
        description="The client requests the same public pages you would open in a browser, parses them, and returns typed models. Your application never touches a selector."
        action={
          <Link
            href="/blog/vlrdevapi-vs-web-scraping/"
            className="group inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
          >
            Why not scrape it yourself?
            <ArrowUpRight
              className="size-3.5 text-[#ff8d97] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        }
      >
        <div className="grid gap-3 lg:grid-cols-3">
          {pipeline.map((step) => (
            <div
              key={step.label}
              className="relative overflow-hidden border border-white/10 bg-[#080808] p-5"
            >
              <span
                aria-hidden="true"
                className="absolute inset-x-0 top-0 h-px bg-[#ff4655]/50"
              />
              <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-[#ff8d97]">
                {step.label}
              </p>
              <h3 className="mt-3 text-lg font-medium tracking-tight text-white">
                {step.title}
              </h3>
              <p className="mt-2 text-[13px] leading-relaxed text-white/40">{step.text}</p>
              <code className="mt-5 block border-t border-white/10 pt-3 font-mono text-[12px] text-white/30">
                {step.detail}
              </code>
            </div>
          ))}
        </div>

        <div className="mt-3 grid gap-3 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="border border-white/10 bg-[#080808] p-5">
            <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
              Built to be a good citizen
            </p>
            <ul className="mt-4 grid gap-2.5 sm:grid-cols-2">
              {[
                'Built-in rate limiting',
                'LRU response cache',
                'Retries for transient failures',
                'Unofficial and independent',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2.5 text-[13px] text-white/50">
                  <span
                    aria-hidden="true"
                    className="mt-1.5 size-1 shrink-0 bg-[#ff4655]"
                  />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-4 border-t border-white/10 pt-3 text-[12px] leading-relaxed text-white/30">
              The SDK does not bypass VLR.gg or Riot access controls. It reads public pages and
              respects a configurable request rate.
            </p>
          </div>

          <div className="border border-white/10 bg-[#080808] p-5">
            <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-3">
              <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                Returned shape
              </p>
              <code className="font-mono text-[12px] text-[#ff8d97]">UpcomingMatchEntry</code>
            </div>
            <dl className="mt-3 space-y-2">
              {returnedFields.map(([field, type]) => (
                <div key={field} className="flex items-center justify-between gap-4">
                  <dt className="min-w-0 truncate font-mono text-[12px] text-white/60">
                    {field}
                  </dt>
                  <dd className="shrink-0 font-mono text-[12px] text-white/25">{type}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </LandingSection>
    </LandingPage>
  );
}
