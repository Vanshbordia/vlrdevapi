import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CodeBlock } from '@/components/landing/code-block';
import { CopyButton } from '@/components/landing/copy-button';
import { LandingPage, LandingSection } from '@/components/landing/landing-page';
import snapshot from '@/components/landing/landing-snapshot.json';
import { canonicalUrl } from '@/lib/shared';

export const metadata: Metadata = {
  title: 'Valorant Stats API for Python',
  description:
    'Get Valorant player, team, and match statistics from VLR.gg in Python. VLRdevAPI returns typed stats models for notebooks, dashboards, and scouting tools.',
  alternates: { canonical: canonicalUrl('/valorant-stats-api/') },
};

const dataframeCode = `import pandas as pd
import vlrdevapi

agents = vlrdevapi.player(11225).agents(timespan="90d")
rows = [agent.model_dump() for agent in agents.agents]

df = pd.DataFrame(rows)
print(df[["agent", "rounds", "rating", "acs"]].head())`;

export default function ValorantStatsApiPage() {
  return (
    <LandingPage
      path="/valorant-stats-api"
      eyebrow="Stats & analytics"
      headline="Valorant Stats API for Python"
      h1={
        <>
          The Valorant stats API for <span className="text-[#ff4655]">Python</span>
        </>
      }
      subtitle="Pull Valorant player, team, and match statistics from VLR.gg in Python. VLRdevAPI returns typed models you can feed straight into a dashboard, notebook, or scouting workflow."
      answer="VLRdevAPI exposes Valorant statistics from VLR.gg as typed Python objects. It covers player agent stats and match history, team map stats and placements, match scoreboards, series round and economy data, and event standings."
      useCases={[
        'pandas notebooks',
        'Polars pipelines',
        'Scouting reports',
        'Fantasy scoring',
        'Team dashboards',
        'Content desks',
      ]}
      capabilitiesTitle="Stats surfaces you can query"
      capabilities={[
        {
          label: 'Player stats',
          bold: 'Profiles and agent usage',
          text: 'Player profiles with top agents, per-agent statistics, and match history across events.',
        },
        {
          label: 'Team stats',
          bold: 'Maps and performance',
          text: 'Map win rates, attack and defense splits, placements, roster history, and transactions.',
        },
        {
          label: 'Match stats',
          bold: 'Scoreboards and maps',
          text: 'Final scores, per-map results, and player scoreboards for completed matches.',
        },
        {
          label: 'Series stats',
          bold: 'Rounds and economy',
          text: 'Round-by-round timelines, performance data, buy types, and economy breakdowns.',
        },
        {
          label: 'Standings',
          bold: 'Groups and points',
          text: 'Event group standings, placements, and circuit points from VCT and regional circuits.',
        },
        {
          label: 'News',
          bold: 'Context and write-ups',
          text: 'The VLR.gg news feed and full articles for background on results.',
        },
      ]}
      quickstart={{
        title: "Read a player's stats without scraping the table.",
        file: 'player_stats.py',
        intro:
          'Use the curried player client for agent stats, then turn the response into rows for analysis. The timespan is a typed literal, not a free-form string.',
        steps: [
          {
            title: 'Pick a player.',
            text: 'Use the VLR.gg player ID with vlrdevapi.player(id).',
          },
          {
            title: 'Choose a timespan.',
            text: '30d, 60d, 90d, or all. The client returns the matching agent slice.',
          },
          {
            title: 'Shape the data.',
            text: 'model_dump() returns dictionaries for pandas, Polars, or plain Python.',
          },
        ],
        code: `import vlrdevapi

player = vlrdevapi.player(11225)
stats = player.agents(timespan="90d")

for agent in stats.agents[:3]:
    print(f"{agent.agent}: {agent.rounds or 0} rounds, {agent.rating or 'N/A'} rating, {agent.acs or 'N/A'} ACS")`,
        outputLabel: 'Example output',
        output: `Kayo: 299 rounds, 1.11 rating, 199.4 ACS
Phoenix: 131 rounds, 0.89 rating, 186.9 ACS
Omen: 103 rounds, 0.89 rating, 151.9 ACS`,
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
          a: 'Yes. The team namespace returns info, rosters, map stats, placements, and transactions.',
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
          a: 'VLRdevAPI reads VLR.gg on each request, so data reflects what VLR.gg currently shows. Responses are cached in-process, so repeated calls stay light.',
        },
        {
          q: 'Is there a free tier?',
          a: 'There are no tiers. The SDK is free and open source, and applies a built-in rate limit so you stay within reasonable request volumes.',
        },
      ]}
      faqIntro="Player, team, and match stats, plus how to move the data into pandas or a dashboard."
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
          href: '/docs/reference/player/agents/',
          label: 'Player agent stats',
          desc: 'Timespans, agent fields, and rating data.',
        },
        {
          href: '/docs/reference/team/stats/',
          label: 'Team stats reference',
          desc: 'Methods and models for team map statistics.',
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
    >
      <LandingSection
        eyebrow="Analysis ready"
        title="Stop copying tables. Start with a DataFrame."
        description="Every stat is already typed and named. Dump the models once, then work in pandas, Polars, or your charting library of choice."
        action={
          <Link
            href="/guides/player-analytics-with-pandas/"
            className="group inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
          >
            Open the pandas guide
            <ArrowUpRight
              className="size-3.5 text-[#ff8d97] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        }
      >
        <div className="grid gap-3 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="overflow-hidden border border-white/10 bg-[#070707]">
            <div className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
              <span className="font-mono text-[12px] text-white/35">player_stats.py</span>
              <CopyButton
                value={dataframeCode}
                label="Copy pandas example"
                className="border-white/10 bg-transparent"
              />
            </div>
            <CodeBlock code={dataframeCode} />
          </div>

          <div className="border border-white/10 bg-[#080808] p-5">
            <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-3">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                  DataFrame preview
                </p>
                <p className="mt-1 text-[13px] text-white/60">
                  {snapshot.player.name} · last 90d
                </p>
              </div>
              <span className="shrink-0 border border-[#ff4655]/30 bg-[#ff4655]/10 px-2 py-1 font-mono text-[12px] text-[#ff8d97]">
                AgentStats
              </span>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[20rem] border-collapse text-left">
                <thead>
                  <tr className="border-b border-white/10">
                    {['Agent', 'Rounds', 'Rating', 'ACS'].map((header, index) => (
                      <th
                        key={header}
                        scope="col"
                        className={`pb-2 font-mono text-[12px] font-normal uppercase tracking-[0.12em] text-white/25 ${
                          index > 0 ? 'text-right' : ''
                        }`}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {snapshot.player.agents.map((agent) => (
                    <tr key={agent.name} className="border-b border-white/10 last:border-b-0">
                      <td className="py-2.5 text-[13px] text-white/70">{agent.name}</td>
                      <td className="py-2.5 text-right font-mono text-[12px] text-white/40">
                        {agent.rounds}
                      </td>
                      <td className="py-2.5 text-right font-mono text-[12px] text-white/40">
                        {agent.rating.toFixed(2)}
                      </td>
                      <td className="py-2.5 text-right font-mono text-[12px] text-white/40">
                        {agent.acs.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="mt-4 border-t border-white/10 pt-3 font-mono text-[12px] text-white/25">
              Source: VLR.gg snapshot · {snapshot.capturedAt}
            </p>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {[
            'model_dump() → DataFrame',
            'No HTML table parsing',
            'Works with pandas and Polars',
            'Typed nullable fields',
          ].map((item) => (
            <span
              key={item}
              className="border border-white/10 px-2.5 py-1 font-mono text-[12px] text-white/35"
            >
              {item}
            </span>
          ))}
        </div>
      </LandingSection>
    </LandingPage>
  );
}
