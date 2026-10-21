'use client';

import Link from 'next/link';
import { ArrowUpRight, FileCode2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { CodeBlock } from './code-block';
import { CopyButton } from './copy-button';

type ModuleId = 'player' | 'team' | 'series' | 'event' | 'news';

const modules: Array<{
  id: ModuleId;
  label: string;
  file: string;
  returns: string;
  href: string;
  code: string;
  methods: string[];
}> = [
  {
    id: 'player',
    label: 'Players',
    file: 'player.py',
    returns: 'PlayerInfo',
    href: '/docs/reference/player/',
    code: `import vlrdevapi

player = vlrdevapi.player(11225)

info = player.info()
agents = player.agents(timespan="60d")

print(info.name, info.country)
print(agents.agents[0].agent)`,
    methods: ['player.info()', 'player.teams()', 'player.agents()', 'player.matches()', 'player.profile()'],
  },
  {
    id: 'team',
    label: 'Teams',
    file: 'team.py',
    returns: 'TeamRoster',
    href: '/docs/reference/team/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    team = client.team(1034)

    print(team.info().name)

    for member in team.roster().players:
        print(member.ign, member.roles)`,
    methods: ['team.info()', 'team.roster()', 'team.placements()', 'team.transactions()', 'team.completed_matches()'],
  },
  {
    id: 'series',
    label: 'Series',
    file: 'series.py',
    returns: 'SeriesInfo',
    href: '/docs/reference/series/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    series = client.series(542272)

    info = series.info()
    rounds = series.rounds(game_id=1)

    print(info.team1.name, info.score1)
    print(info.team2.name, info.score2)
    print(len(rounds.rounds), "rounds parsed")`,
    methods: ['series.info()', 'series.rounds()', 'series.players()', 'series.economy()', 'series.vods()'],
  },
  {
    id: 'event',
    label: 'Events',
    file: 'event.py',
    returns: 'EventStages',
    href: '/docs/reference/events/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    event = client.event(2863)

    print(event.info().name)

    for stage in event.stages():
        print(stage.name)

    standings = event.standings()`,
    methods: ['event.info()', 'event.stages()', 'event.matches()', 'event.standings()', 'event.teams()'],
  },
  {
    id: 'news',
    label: 'News',
    file: 'news.py',
    returns: 'Article',
    href: '/docs/reference/news/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    page = client.news(page=1)

    for item in page.news[:3]:
        print(item.title)

    article = client.news.article(page.news[0].id)
    print(article.content_md[:500])`,
    methods: ['client.news()', 'client.news.article()'],
  },
];

function displayModelName(value: string) {
  return value.replace(/([a-z0-9])([A-Z])/g, '$1 $2');
}

export function HeroDemo() {
  const [activeId, setActiveId] = useState<ModuleId>('player');
  const [paused, setPaused] = useState(false);
  const active = modules.find((item) => item.id === activeId) ?? modules[0];

  useEffect(() => {
    if (paused) return;
    const interval = setInterval(() => {
      setActiveId((current) => {
        const index = modules.findIndex((item) => item.id === current);
        return modules[(index + 1) % modules.length].id;
      });
    }, 7000);
    return () => clearInterval(interval);
  }, [paused]);

  return (
    <div className="relative min-w-0 max-w-full" data-hero-demo>
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-8 -z-10 bg-[radial-gradient(55%_55%_at_60%_30%,rgba(255,70,85,0.14),transparent_72%)] blur-2xl"
      />

      {/* Tactical corner ticks */}
      <span aria-hidden="true" className="absolute -left-2 -top-2 hidden size-4 border-l border-t border-[#ff4655]/60 sm:block" />
      <span aria-hidden="true" className="absolute -right-2 -top-2 hidden size-4 border-r border-t border-white/25 sm:block" />
      <span aria-hidden="true" className="absolute -bottom-2 -left-2 hidden size-4 border-b border-l border-white/25 sm:block" />
      <span aria-hidden="true" className="absolute -bottom-2 -right-2 hidden size-4 border-b border-r border-[#ff4655]/60 sm:block" />

      <div
        className="relative w-full min-w-0 overflow-hidden border border-white/10 bg-[#080808] shadow-[0_40px_120px_-40px_rgba(0,0,0,1)]"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
        onFocusCapture={() => setPaused(true)}
        onBlurCapture={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
            setPaused(false);
          }
        }}
      >
        <div className="relative border-b border-white/10">
          <div className="grid grid-cols-5 gap-1 p-1.5">
            {modules.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveId(item.id)}
                aria-pressed={activeId === item.id}
                className={`relative w-full border px-1.5 py-1.5 text-center text-[12px] font-medium transition-colors sm:px-3 sm:text-[12.5px] ${
                  activeId === item.id
                    ? 'border-white/15 bg-white/[0.08] text-white'
                    : 'border-transparent text-white/40 hover:bg-white/[0.04] hover:text-white/75'
                }`}
              >
                {item.label}
                {activeId === item.id ? (
                  <span
                    aria-hidden="true"
                    className="absolute inset-x-2 bottom-0 h-px bg-[#ff4655]"
                  />
                ) : null}
              </button>
            ))}
          </div>
          <div aria-hidden="true" className="absolute inset-x-0 bottom-0 h-px bg-white/[0.04]">
            <div
              key={activeId}
              className="h-full origin-left animate-[landing-progress_7s_linear_forwards] bg-[#ff4655]/80"
              style={{ animationPlayState: paused ? 'paused' : 'running' }}
            />
          </div>
        </div>

        <div className="relative flex items-center justify-between gap-3 border-b border-white/10 px-3.5 py-2.5">
          <div className="flex min-w-0 items-center gap-2">
            <FileCode2 className="size-3.5 shrink-0 text-[#ff4655]" aria-hidden="true" />
            <span className="truncate font-mono text-[12px] text-white/50">{active.file}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden border border-white/10 px-1.5 py-0.5 font-mono text-[12px] text-white/35 sm:inline">
              Python 3.11+
            </span>
            <CopyButton value={active.code} label={`Copy ${active.file}`} />
          </div>
        </div>

        <div className="h-[282px] min-w-0 overflow-hidden">
          <CodeBlock
            key={activeId}
            code={active.code}
            animate
            className="[scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          />
        </div>

        <div className="flex min-w-0 items-center justify-between gap-4 border-t border-white/10 bg-white/[0.02] px-4 py-3">
          <div className="flex min-w-0 items-center gap-2">
            <span className="relative flex size-1.5 shrink-0">
              <span className="absolute inline-flex size-full animate-[landing-pulse_2.4s_ease-in-out_infinite] rounded-full bg-[#ff4655]" />
              <span className="relative inline-flex size-1.5 rounded-full bg-[#ff4655]" />
            </span>
            <span className="truncate font-mono text-[12px] uppercase tracking-[0.14em] text-white/35">
              returns <span className="text-white/70">{displayModelName(active.returns)}</span>
            </span>
          </div>
          <Link
            href={active.href}
            className="group inline-flex shrink-0 items-center gap-1 text-[12px] font-medium text-white/55 transition-colors hover:text-white"
          >
            {active.label} reference
            <ArrowUpRight
              className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        </div>
      </div>

      <div className="mt-3 flex h-7 min-w-0 items-center gap-1.5">
        <div className="relative min-w-0 flex-1">
          <div className="flex h-7 min-w-0 items-center gap-1.5 overflow-x-auto pr-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {active.methods.map((method) => (
              <code
                key={method}
                className="shrink-0 border border-white/10 bg-white/[0.02] px-2.5 py-1 font-mono text-[12px] text-white/45"
              >
                {method}
              </code>
            ))}
          </div>
          <span
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 right-0 w-6 bg-gradient-to-l from-black to-transparent"
          />
        </div>
        <Link
          href="/docs/reference/"
          className="group ml-1 inline-flex shrink-0 items-center gap-1 px-1 text-[12px] font-medium text-white/40 transition-colors hover:text-white"
        >
          All namespaces
          <ArrowUpRight
            className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      </div>
    </div>
  );
}
