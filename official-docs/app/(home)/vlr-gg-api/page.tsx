import type { Metadata } from 'next';
import { LandingPage } from '@/components/landing/landing-page';
import { canonicalUrl } from '@/lib/shared';

export const metadata: Metadata = {
  title: 'VLR.gg API for Python (Unofficial)',
  description:
    'VLR.gg has no public API. VLRdevAPI is a free, typed Python SDK that fetches matches, players, teams, and events from VLR.gg with no API key.',
  alternates: { canonical: canonicalUrl('/vlr-gg-api/') },
};

export default function VlrGgApiPage() {
  return (
    <LandingPage
      path="/vlr-gg-api"
      eyebrow="VLR.gg API"
      headline="VLR.gg API for Python"
      h1={
        <>
          The VLR.gg API for <span className="text-fd-primary">Python</span>
        </>
      }
      subtitle="VLR.gg does not publish a public API. VLRdevAPI is a free, open-source Python SDK that reads VLR.gg for you and returns typed objects, so you can query Valorant esports data without writing or maintaining a scraper."
      answer="Short answer: VLR.gg has no official API. VLRdevAPI is an unofficial Python client that fetches and parses VLR.gg pages, then returns Pydantic models. It needs no API key and runs on Python 3.11 or newer."
      capabilitiesTitle="What you can fetch from VLR.gg"
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
        intro:
          'Install the package with pip, then fetch upcoming matches. Each match is a typed object with teams, event, stage, and start time.',
        code: `import vlrdevapi

page = vlrdevapi.matches.upcoming()
for match in page.matches[:3]:
    team1 = match.team1.name if match.team1 else "TBD"
    team2 = match.team2.name if match.team2 else "TBD"
    print(f"{team1} vs {team2} | {match.event}")`,
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
          a: 'The client applies a built-in rate limit and caches responses. Both are configurable, and multi-stage endpoints fetch their pages in parallel.',
        },
      ]}
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
    />
  );
}
