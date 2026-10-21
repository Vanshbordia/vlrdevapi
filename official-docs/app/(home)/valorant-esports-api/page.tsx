import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { CodeBlock } from '@/components/landing/code-block';
import { CopyButton } from '@/components/landing/copy-button';
import { LandingPage, LandingSection } from '@/components/landing/landing-page';
import snapshot from '@/components/landing/landing-snapshot.json';
import { createPageMetadata } from '@/lib/seo';

export const metadata: Metadata = createPageMetadata({
  title: 'Valorant Esports API for Python',
  description:
    'Query Valorant esports data from VLR.gg in Python. VLRdevAPI returns typed matches, event stages, standings, rosters, series, and round data. Free, with no API key.',
  path: '/valorant-esports-api/',
});

const flow = [
  {
    step: '01',
    title: 'Event',
    method: 'event.info()',
    text: 'Name, region, venue, dates, and the tournament context.',
  },
  {
    step: '02',
    title: 'Stage',
    method: 'event.stages()',
    text: 'Group stage, playoffs, Swiss, or whatever VLR.gg lists.',
  },
  {
    step: '03',
    title: 'Match',
    method: 'event.matches()',
    text: 'Schedule, teams, scores, and the stage each match belongs to.',
  },
  {
    step: '04',
    title: 'Series',
    method: 'series.rounds(game_id=1)',
    text: 'Maps, round timeline, economy data, player stats, and VODs.',
  },
];

const eventWalkCode = `import vlrdevapi

event = vlrdevapi.event(2863)
print(event.info().name)

for stage in event.stages():
    print(stage.name)

standings = event.standings()
for row in standings.stages[0].standings[:3]:
    print(row.place, row.team.name, row.points)`;

export default function ValorantEsportsApiPage() {
  return (
    <LandingPage
      path="/valorant-esports-api"
      eyebrow="Esports data"
      headline="Valorant Esports API for Python"
      h1={
        <>
          The Valorant esports API for <span className="text-[#ff4655]">Python</span>
        </>
      }
      subtitle="Query Valorant esports data from VLR.gg in Python. VLRdevAPI returns matches, results, standings, rosters, players, and event data as typed models. Free, and no API key required."
      answer="VLRdevAPI is a free, typed Python API for Valorant esports data. It covers VCT and regional competition data on VLR.gg, including upcoming and completed matches, live scores, event stages, group standings, team rosters, series round data, and player statistics."
      useCases={[
        'Match tickers',
        'Bracket viewers',
        'Standings widgets',
        'Roster trackers',
        'Live alerts',
        'Esports sites',
      ]}
      capabilitiesTitle="Esports surfaces you can query"
      capabilities={[
        {
          label: 'Matches and results',
          bold: 'Upcoming, live, and completed',
          text: 'Match schedules, live scores, and final results with per-map scoreboards.',
        },
        {
          label: 'Standings',
          bold: 'Groups and placements',
          text: 'Event group tables, team placements, circuit points, and stage-by-stage standings.',
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
        title: 'Start with the next match, not the HTML.',
        file: 'next_match.py',
        intro:
          'VLRdevAPI keeps the tournament hierarchy intact. Start from the schedule, then move into an event or series when you need more depth.',
        steps: [
          {
            title: 'Find the next match.',
            text: 'matches.upcoming() returns the next page of scheduled matches.',
          },
          {
            title: 'Open the event.',
            text: 'Pass an event ID into event() to read its stages and standings.',
          },
          {
            title: 'Drill into the series.',
            text: 'Use series IDs for maps, rounds, economy, player stats, and VODs.',
          },
        ],
        code: `import vlrdevapi

page = vlrdevapi.matches.upcoming()
match = page.matches[0]

team1 = match.team1.name if match.team1 else "TBD"
team2 = match.team2.name if match.team2 else "TBD"

print(match.event, "·", match.stage)
print(team1, "vs", team2)

event = vlrdevapi.event(2863)
for stage in event.stages():
    print(stage.name)`,
        outputLabel: 'Example output',
        output: `VCT 2026: EMEA Stage 1 · Playoffs
NRG vs FNATIC
Playoffs
Group Stage`,
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
          a: 'VLRdevAPI reads VLR.gg on each request, so results reflect what VLR.gg currently shows. Responses are cached in-process, so repeated calls stay light.',
        },
      ]}
      faqIntro="Coverage, live scores, VCT, and the difference between esports results and Riot match data."
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
    >
      <LandingSection
        eyebrow="Tournament flow"
        title="One event ID opens the bracket."
        description="Start at the event, move through its stages, then drill into matches, series, and round data. The models keep the hierarchy intact."
        action={
          <Link
            href="/guides/building-a-real-time-match-monitor/"
            className="group inline-flex items-center gap-1.5 text-[12.5px] font-medium text-white/50 transition-colors hover:text-white"
          >
            Build a live monitor
            <ArrowUpRight
              className="size-3.5 text-[#ff8d97] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        }
      >
        <ol className="grid gap-3 md:grid-cols-4">
          {flow.map((item) => (
            <li
              key={item.step}
              className="relative overflow-hidden border border-white/10 bg-[#080808] p-4"
            >
              <span
                aria-hidden="true"
                className="absolute right-0 top-0 size-1.5 bg-[#ff4655]/60"
              />
              <p className="font-mono text-[12px] text-[#ff4655]">{item.step}</p>
              <h3 className="mt-4 text-[15px] font-medium tracking-tight text-white">
                {item.title}
              </h3>
              <p className="mt-1.5 text-[12.5px] leading-relaxed text-white/40">{item.text}</p>
              <code className="mt-4 block border-t border-white/10 pt-3 font-mono text-[12px] text-white/30">
                {item.method}
              </code>
            </li>
          ))}
        </ol>

        <div className="mt-3 grid gap-3 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="overflow-hidden border border-white/10 bg-[#070707]">
            <div className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
              <span className="font-mono text-[12px] text-white/35">event_walk.py</span>
              <CopyButton
                value={eventWalkCode}
                label="Copy event example"
                className="border-white/10 bg-transparent"
              />
            </div>
            <CodeBlock code={eventWalkCode} />
          </div>

          <div className="border border-white/10 bg-[#080808] p-5">
            <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-3">
              <div>
                <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">
                  Playoffs standings
                </p>
                <p className="mt-1 text-[13px] text-white/60">{snapshot.event.name}</p>
              </div>
              <span className="shrink-0 font-mono text-[12px] text-white/25">event 2863</span>
            </div>

            <div className="mt-3 space-y-1.5">
              {snapshot.event.standings.map((row) => (
                <div
                  key={row.team}
                  className="flex items-center gap-3 border border-white/[0.07] bg-white/[0.02] px-3 py-2"
                >
                  <span className="w-7 shrink-0 font-mono text-[12px] text-[#ff8d97]">
                    {row.place}
                  </span>
                  <span className="min-w-0 flex-1 truncate text-[13px] text-white/70">
                    {row.team}
                  </span>
                  <span className="font-mono text-[12px] text-white/30">{row.points} pts</span>
                </div>
              ))}
            </div>

            <p className="mt-4 border-t border-white/10 pt-3 font-mono text-[12px] text-white/25">
              event.standings().stages[0].standings
            </p>
          </div>
        </div>
      </LandingSection>
    </LandingPage>
  );
}
