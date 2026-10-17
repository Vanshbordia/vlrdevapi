import type { Metadata } from 'next';
import { LandingPage } from '@/components/landing/landing-page';
import { canonicalUrl } from '@/lib/shared';

export const metadata: Metadata = {
  title: 'Valorant Stats API for Python',
  description:
    'Get Valorant player, team, and match statistics from VLR.gg in Python. VLRdevAPI returns typed stats models for dashboards and notebooks, free and with no API key.',
  alternates: { canonical: canonicalUrl('/valorant-stats-api/') },
};

export default function ValorantStatsApiPage() {
  return (
    <LandingPage
      path="/valorant-stats-api"
      eyebrow="Stats"
      headline="Valorant Stats API for Python"
      h1={
        <>
          The Valorant stats API for <span className="text-fd-primary">Python</span>
        </>
      }
      subtitle="Pull Valorant player, team, and match statistics from VLR.gg in Python. VLRdevAPI returns typed models you can feed straight into a dashboard or notebook."
      answer="VLRdevAPI exposes Valorant statistics from VLR.gg as typed Python objects. It covers player agent stats and match history, team stats and placements, match scoreboards, and series-level round and economy data."
      capabilitiesTitle="Statistics you can query"
      capabilities={[
        {
          label: 'Player stats',
          bold: 'Profiles and agent usage',
          text: 'Player profiles with top agents, per-agent statistics, and match history across events.',
        },
        {
          label: 'Team stats',
          bold: 'Performance and placement',
          text: 'Aggregate team stats, event placements, roster history, and transactions.',
        },
        {
          label: 'Match stats',
          bold: 'Scoreboards and maps',
          text: 'Final scores, per-map results, and player scoreboards for completed matches.',
        },
        {
          label: 'Series stats',
          bold: 'Rounds and economy',
          text: 'Round-by-round timelines, performance data, and economy breakdowns for a series.',
        },
        {
          label: 'Standings',
          bold: 'Groups and tables',
          text: 'Event group standings and stage tables from VCT and regional circuits.',
        },
        {
          label: 'News',
          bold: 'Context and write-ups',
          text: 'The VLR.gg news feed and full articles for background on results.',
        },
      ]}
      quickstart={{
        intro:
          'Install the package and read a player profile. Stats arrive as typed models, ready to convert into a DataFrame or render in a dashboard.',
        code: `import vlrdevapi

profile = vlrdevapi.player(438).profile()
print(f"{profile.name} - {', '.join(a.agent for a in profile.top_agents[:3])}")`,
      }}
      comparison={{
        title: 'Getting Valorant stats in Python',
        headers: ['', 'VLRdevAPI', 'Scraping tables', 'Manual copy'],
        rows: [
          ['Data', 'Player, team, match, series stats', 'Whichever tables you parse', 'Whatever you copy by hand'],
          ['Format', 'Typed models', 'HTML tables', 'Spreadsheets'],
          ['Refresh', 'Re-fetch with one call', 'Re-scrape and re-parse', 'Manual'],
          ['Rate limiting', 'Built in', 'Your responsibility', 'Not applicable'],
          ['Maintenance', 'Handled in the library', 'High', 'Manual'],
        ],
      }}
      faqs={[
        {
          q: 'What player statistics are available?',
          a: 'Player profiles include name, country, team, and top agents, plus agent statistics and match history across events.',
        },
        {
          q: 'Can I get team statistics?',
          a: 'Yes. The team namespace returns info, rosters, stats, placements, and transactions.',
        },
        {
          q: 'Is match scoreboard data included?',
          a: 'Yes. Completed matches include scores and per-map results, and series data adds round-by-round and economy statistics.',
        },
        {
          q: 'Can I build a dashboard with this?',
          a: 'Yes. Every response is a Pydantic model, so you can convert it to dictionaries or DataFrames and render it with any Python web or charting library.',
        },
        {
          q: 'How current is the data?',
          a: 'VLRdevAPI reads VLR.gg on each request, so data reflects what VLR.gg currently shows. Responses are cached briefly and the cache is configurable.',
        },
        {
          q: 'Is there a free tier?',
          a: 'There are no tiers. The SDK is free and open source, and applies a built-in rate limit so you stay within reasonable request volumes.',
        },
      ]}
      related={[
        {
          href: '/guides/player-analytics-with-pandas/',
          label: 'Player analytics with pandas',
          desc: 'Load stats into a DataFrame and analyze them.',
        },
        {
          href: '/guides/event-analytics-with-polars/',
          label: 'Event analytics with Polars',
          desc: 'Analyze event and match data with Polars.',
        },
        {
          href: '/docs/reference/player/',
          label: 'Player reference',
          desc: 'Methods and models for player data.',
        },
        {
          href: '/docs/reference/team/stats/',
          label: 'Team stats reference',
          desc: 'Methods and models for team statistics.',
        },
        {
          href: '/valorant-esports-api/',
          label: 'Valorant esports API',
          desc: 'The full set of esports data in Python.',
        },
        {
          href: '/valorant-api-python/',
          label: 'Valorant API for Python',
          desc: 'Install and work with typed models.',
        },
      ]}
    />
  );
}
