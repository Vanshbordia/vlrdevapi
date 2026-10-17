import type { Metadata } from 'next';
import { LandingPage } from '@/components/landing/landing-page';
import { canonicalUrl } from '@/lib/shared';

export const metadata: Metadata = {
  title: 'Valorant Esports API for Python',
  description:
    'Query Valorant esports data from VLR.gg in Python. VLRdevAPI returns typed matches, results, standings, rosters, and player stats. Free, with no API key.',
  alternates: { canonical: canonicalUrl('/valorant-esports-api/') },
};

export default function ValorantEsportsApiPage() {
  return (
    <LandingPage
      path="/valorant-esports-api"
      eyebrow="Valorant esports API"
      headline="Valorant Esports API for Python"
      h1={
        <>
          The Valorant esports API for <span className="text-fd-primary">Python</span>
        </>
      }
      subtitle="Query Valorant esports data from VLR.gg in Python. VLRdevAPI returns matches, results, standings, rosters, players, and event data as typed models. Free, and no API key required."
      answer="VLRdevAPI is a free, typed Python API for Valorant esports data. It covers VCT and regional competition data on VLR.gg, including upcoming and completed matches, live scores, group standings, team rosters, and player statistics."
      capabilitiesTitle="Esports data you can query"
      capabilities={[
        {
          label: 'Matches and results',
          bold: 'Upcoming, live, and completed',
          text: 'Match schedules, live scores, and final results with per-map scoreboards.',
        },
        {
          label: 'Standings',
          bold: 'Groups and placements',
          text: 'Event group tables, team placements, and stage-by-stage standings.',
        },
        {
          label: 'Teams',
          bold: 'Rosters and history',
          text: 'Team info, active rosters, aggregate stats, placements, and transactions.',
        },
        {
          label: 'Players',
          bold: 'Profiles and agent stats',
          text: 'Player profiles, top agents, agent statistics, and match history.',
        },
        {
          label: 'Events',
          bold: 'Tournaments and stages',
          text: 'Event listings, stages, participating teams, and match schedules.',
        },
        {
          label: 'Series',
          bold: 'VODs and round data',
          text: 'Series info, VOD links, round timelines, performance, and economy data.',
        },
      ]}
      quickstart={{
        intro:
          'The same pattern works across every namespace. Install the package, then read upcoming matches or drill into a specific team.',
        code: `import vlrdevapi

page = vlrdevapi.matches.upcoming()
for match in page.matches[:3]:
    team1 = match.team1.name if match.team1 else "TBD"
    team2 = match.team2.name if match.team2 else "TBD"
    print(f"{team1} vs {team2} | {match.event}")`,
      }}
      comparison={{
        title: 'Where does the data come from?',
        headers: ['', 'VLRdevAPI', 'Riot official API', 'Community JSON services'],
        rows: [
          ['Coverage', 'Pro esports results, standings, rosters', 'Account and in-game match data', 'Varies by service'],
          ['Source', 'VLR.gg', 'Riot', 'Unofficial scrapers'],
          ['Output', 'Typed Pydantic models', 'Riot JSON', 'Custom JSON'],
          ['API key', 'Not required', 'Required', 'Sometimes required'],
          ['Cost', 'Free', 'Free tier with limits', 'Varies'],
          ['Maintenance', 'Handled in the library', 'Riot-maintained', 'Varies'],
        ],
      }}
      faqs={[
        {
          q: 'Is there a Valorant esports API?',
          a: 'Riot does not publish a general esports results API. VLRdevAPI provides one for Python by reading VLR.gg, which tracks professional Valorant matches and events.',
        },
        {
          q: 'What esports data can I access?',
          a: 'Upcoming, live, and completed matches with scores; event stages and standings; team rosters, stats, and placements; player profiles and agent stats; series, VODs, and round data; and news articles.',
        },
        {
          q: 'Does it cover VCT?',
          a: 'Yes. VLR.gg tracks VCT and regional Valorant circuits, and VLRdevAPI returns whatever VLR.gg lists, including event stages and standings.',
        },
        {
          q: 'Can I get live match data?',
          a: 'Yes. vlrdevapi.matches.live() returns matches that are currently in progress.',
        },
        {
          q: 'Do I need a Riot API key?',
          a: 'No. VLRdevAPI does not use the Riot API and does not require a key of any kind.',
        },
        {
          q: 'How current is the data?',
          a: 'VLRdevAPI reads VLR.gg on each request, so results reflect what VLR.gg currently shows. Responses are cached briefly and the cache is configurable.',
        },
      ]}
      related={[
        {
          href: '/vlr-gg-api/',
          label: 'VLR.gg API for Python',
          desc: 'Why an unofficial client exists and what it covers.',
        },
        {
          href: '/valorant-api-python/',
          label: 'Valorant API for Python',
          desc: 'Install the SDK and work with typed models.',
        },
        {
          href: '/valorant-stats-api/',
          label: 'Valorant stats API',
          desc: 'Player, team, and match statistics in Python.',
        },
        {
          href: '/docs/',
          label: 'Documentation',
          desc: 'Guides and the full API reference.',
        },
        {
          href: '/guides/building-a-real-time-match-monitor/',
          label: 'Build a match monitor',
          desc: 'Track live Valorant matches with Python.',
        },
        {
          href: '/blog/vlrdevapi-vs-other-valorant-apis/',
          label: 'How the options compare',
          desc: 'VLRdevAPI against other Valorant data sources.',
        },
      ]}
    />
  );
}
