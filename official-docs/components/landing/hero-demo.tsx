'use client';

import Link from 'next/link';
import { ArrowUpRight, FileCode2 } from 'lucide-react';
import { useState } from 'react';
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
    href: '/docs/reference/player',
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
    href: '/docs/reference/team',
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
    href: '/docs/reference/series',
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
    href: '/docs/reference/events',
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
    href: '/docs/reference/news',
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
  const active = modules.find((item) => item.id === activeId) ?? modules[0];

  return (
    <div className="relative min-w-0 max-w-full">
      <div className="relative w-full min-w-0 overflow-hidden border border-white/10 bg-fd-panel">
        <div className="relative border-b border-white/10">
          <div role="tablist" aria-label="SDK namespaces" className="grid grid-cols-5 gap-px bg-white/10">
            {modules.map((item) => {
              const selected = activeId === item.id;

              return (
                <button
                  key={item.id}
                  type="button"
                  role="tab"
                  id={`hero-tab-${item.id}`}
                  aria-selected={selected}
                  aria-controls="hero-demo-panel"
                  tabIndex={selected ? 0 : -1}
                  onClick={() => setActiveId(item.id)}
                  onKeyDown={(event) => {
                    const index = modules.findIndex((entry) => entry.id === activeId);

                    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
                      event.preventDefault();
                      const offset = event.key === 'ArrowRight' ? 1 : -1;
                      const next = modules[(index + offset + modules.length) % modules.length];
                      setActiveId(next.id);
                      document.getElementById(`hero-tab-${next.id}`)?.focus();
                    }
                  }}
                  className={`relative bg-fd-panel px-1.5 py-2.5 text-center text-[12px] font-medium transition-colors sm:px-3 sm:text-[12.5px] ${
                    selected ? 'text-white' : 'text-fd-muted hover:text-white/80'
                  }`}
                >
                  {item.label}
                  {selected ? (
                    <span
                      aria-hidden="true"
                      className="absolute inset-x-0 bottom-0 h-px bg-fd-primary"
                    />
                  ) : null}
                </button>
              );
            })}
          </div>
        </div>

        <div className="relative flex items-center justify-between gap-3 border-b border-white/10 px-3.5 py-2.5">
          <div className="flex min-w-0 items-center gap-2">
            <FileCode2 className="size-3.5 shrink-0 text-fd-muted" aria-hidden="true" />
            <span className="truncate font-mono text-[12px] text-white/50">{active.file}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden font-mono text-[12px] text-fd-muted sm:inline">Python 3.11+</span>
            <CopyButton value={active.code} label={`Copy ${active.file}`} />
          </div>
        </div>

        <div
          id="hero-demo-panel"
          role="tabpanel"
          aria-labelledby={`hero-tab-${activeId}`}
          tabIndex={0}
          className="h-[282px] min-w-0 overflow-hidden"
        >
          <CodeBlock
            key={activeId}
            code={active.code}
            animate
            className="[scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          />
        </div>

        <div className="flex min-w-0 items-center justify-between gap-4 border-t border-white/10 bg-white/[0.02] px-4 py-3">
          <span className="truncate font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
            returns <span className="text-white/75">{displayModelName(active.returns)}</span>
          </span>
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
                className="shrink-0 border border-white/10 bg-white/[0.02] px-2.5 py-1 font-mono text-[12px] text-fd-subtle"
              >
                {method}
              </code>
            ))}
          </div>
          <span
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 right-0 w-6 bg-gradient-to-l from-fd-canvas to-transparent"
          />
        </div>
        <Link
          href="/docs/reference/"
          className="group ml-1 inline-flex shrink-0 items-center gap-1 px-1 text-[12px] font-medium text-fd-muted transition-colors hover:text-white"
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
