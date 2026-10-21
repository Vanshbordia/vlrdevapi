'use client';

import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { useEffect, useState, type MouseEvent, type ReactNode } from 'react';
import snapshot from './landing-snapshot.json';
import { CodeBlock } from './code-block';
import { CopyButton } from './copy-button';
import { Reveal } from './reveal';

type ModuleId = 'player' | 'team' | 'series' | 'event' | 'news';

const modules: Array<{
  id: ModuleId;
  label: string;
  blurb: string;
  file: string;
  returns: string;
  href: string;
  code: string;
  methods: string[];
}> = [
  {
    id: 'player',
    label: 'Players',
    blurb: 'Profiles, career teams, agent stats, placements, and match history.',
    file: 'player.py',
    returns: 'PlayerProfile',
    href: '/docs/reference/player/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    player = client.player(11225)

    info = player.info()
    teams = player.teams()
    agents = player.agents(timespan="90d")

    print(info.name, info.country)
    print(teams.current_teams[0].name)
    print(agents.agents[0].agent)`,
    methods: ['info()', 'teams()', 'agents()', 'matches()', 'placements()', 'profile()'],
  },
  {
    id: 'team',
    label: 'Teams',
    blurb: 'Rosters, staff, placements, prize money, and full match history.',
    file: 'team.py',
    returns: 'TeamPlacements',
    href: '/docs/reference/team/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    team = client.team(1034)

    print(team.info().name)

    for member in team.roster().players:
        print(member.ign, member.roles)

    for placement in team.placements().placements[:3]:
        print(placement.event_name)
        print(placement.placements[0].placement)`,
    methods: ['info()', 'roster()', 'placements()', 'transactions()', 'stats()', 'completed_matches()'],
  },
  {
    id: 'series',
    label: 'Series',
    blurb: 'Scores, map vetoes, round data, player stats, economy, and VODs.',
    file: 'series.py',
    returns: 'EconomyData',
    href: '/docs/reference/series/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    series = client.series(542272)

    info = series.info()
    rounds = series.rounds(game_id=1)
    economy = series.economy(game_id=1)

    print(f"{info.team1.name} {info.score1}-{info.score2}")
    print(len(rounds.rounds), "rounds")
    print(economy.rounds[0].winner.name)`,
    methods: ['info()', 'rounds()', 'players()', 'performance()', 'economy()', 'vods()'],
  },
  {
    id: 'event',
    label: 'Events',
    blurb: 'Event metadata, stages, brackets, matches, and final standings.',
    file: 'event.py',
    returns: 'EventStandings',
    href: '/docs/reference/events/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    event = client.event(2863)

    print(event.info().name)

    for stage in event.stages():
        print(stage.name)

    standings = event.standings()
    for row in standings.stages[0].standings[:3]:
        print(row.place, row.team.name)`,
    methods: ['info()', 'stages()', 'matches()', 'teams()', 'standings()'],
  },
  {
    id: 'news',
    label: 'News',
    blurb: 'The latest headlines and full articles, converted to clean Markdown.',
    file: 'news.py',
    returns: 'NewsArticle',
    href: '/docs/reference/news/',
    code: `from vlrdevapi import VLRClient

with VLRClient() as client:
    page = client.news(page=1)

    for article in page.news[:3]:
        print(article.title)

    full = client.news.article(page.news[0].id)
    print(full.author, full.date)
    print(full.content_md[:500])`,
    methods: ['news()', 'news.article()'],
  },
];

const shortDate = (value: string) =>
  new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${value}T00:00:00Z`));

const shortDateFromIso = (value: string) =>
  new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(value));

const dateRange = (start: string, end: string) =>
  start === end ? shortDate(start) : `${shortDate(start)} – ${shortDate(end)}`;

const formatMoney = (value: number, currency: string) =>
  `${currency}${new Intl.NumberFormat('en-US').format(value)}`;

function displayModelName(value: string) {
  return value.replace(/([a-z0-9])([A-Z])/g, '$1 $2');
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-white/10 bg-white/[0.02] px-3 py-2.5">
      <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/35">{label}</p>
      <p className="mt-1 font-mono text-lg text-white">{value}</p>
    </div>
  );
}

function PreviewShell({
  eyebrow,
  title,
  meta,
  badge,
  children,
}: {
  eyebrow: string;
  title: string;
  meta: string;
  badge: string;
  children: ReactNode;
}) {
  return (
    <div className="flex h-full flex-col p-4 sm:p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="font-mono text-[12px] uppercase tracking-[0.16em] text-white/30">{eyebrow}</p>
          <h4 className="mt-1.5 truncate text-lg font-medium tracking-tight text-white">{title}</h4>
          <p className="mt-0.5 text-[12.5px] text-white/45">{meta}</p>
        </div>
        <span className="shrink-0 border border-[#ff4655]/30 bg-[#ff4655]/10 px-2.5 py-1 font-mono text-[12px] text-[#ff8d97]">
          {displayModelName(badge)}
        </span>
      </div>
      <div className="mt-5 flex-1">{children}</div>
      <p className="mt-5 border-t border-white/10 pt-3 font-mono text-[12px] uppercase tracking-[0.14em] text-white/25">
        Live VLR.gg snapshot · {snapshot.capturedAt}
      </p>
    </div>
  );
}

function Preview({ id }: { id: ModuleId }) {
  if (id === 'player') {
    const topAgent = snapshot.player.agents[0];

    return (
      <PreviewShell
        eyebrow="Player profile"
        title={snapshot.player.name}
        meta={`${snapshot.player.realName} · ${snapshot.player.country}`}
        badge="PlayerInfo"
      >
        <div className="flex items-center justify-between gap-3">
          <p className="font-mono text-[12px] uppercase tracking-[0.12em] text-white/30">
            Top agent · 90d
          </p>
          <p className="font-mono text-[12px] text-white/35">
            {topAgent.name} · {topAgent.rounds} rounds
          </p>
        </div>
        <div className="mt-2 grid grid-cols-3 gap-2">
          <Stat label="Rating" value={topAgent.rating.toFixed(2)} />
          <Stat label="ACS" value={topAgent.acs.toFixed(1)} />
          <Stat label="K / D" value={topAgent.kd.toFixed(2)} />
        </div>
        <div className="mt-4 space-y-2.5">
          {snapshot.player.agents.map((agent) => (
            <div key={agent.name}>
              <div className="flex items-center justify-between text-[12px]">
                <span className="text-white/65">{agent.name}</span>
                <span className="font-mono text-white/35">{agent.share}</span>
              </div>
              <div className="mt-1 h-1 overflow-hidden bg-white/[0.06]">
                <div className="h-full bg-white/35" style={{ width: agent.share }} />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3">
          <span className="text-[12px] text-white/40">Career winnings</span>
          <span className="font-mono text-[12px] text-white/70">
            {formatMoney(snapshot.player.totalWinnings, snapshot.player.currency)}
          </span>
        </div>
      </PreviewShell>
    );
  }

  if (id === 'team') {
    return (
      <PreviewShell
        eyebrow="Team profile"
        title={snapshot.team.name}
        meta={`${snapshot.team.country} · ${snapshot.team.players.length} players · ${snapshot.team.staff.length} staff`}
        badge="TeamRoster"
      >
        <div className="space-y-1.5">
          {snapshot.team.players.map((player, index) => (
            <div
              key={player.id}
              className="flex items-center justify-between border border-white/[0.07] bg-white/[0.02] px-3 py-2"
            >
              <div className="flex items-center gap-2.5">
                <span className="flex size-6 items-center justify-center bg-white/[0.06] font-mono text-[12px] text-white/50">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <span className="font-mono text-[12px] text-white/70">{player.ign}</span>
              </div>
              <span
                className={`text-[12px] ${
                  player.role === 'Captain' ? 'text-[#ff9aa2]' : 'text-white/35'
                }`}
              >
                {player.role}
              </span>
            </div>
          ))}
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3 border-t border-white/10 pt-3">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.1em] text-white/25">
              Winnings
            </p>
            <p className="mt-0.5 font-mono text-[12px] text-white/65">
              {formatMoney(snapshot.team.totalWinnings, snapshot.team.currency)}
            </p>
          </div>
          <div className="min-w-0 text-right">
            <p className="font-mono text-[12px] uppercase tracking-[0.1em] text-white/25">
              Best result
            </p>
            <p className="mt-0.5 truncate font-mono text-[12px] text-white/65">
              Champions 2025 · {snapshot.team.highlight.placement}
            </p>
          </div>
        </div>
      </PreviewShell>
    );
  }

  if (id === 'series') {
    const series = snapshot.series;

    return (
      <PreviewShell
        eyebrow="Series overview"
        title={`${series.team1} vs ${series.team2}`}
        meta={`${series.event} · ${series.bracket}`}
        badge="SeriesInfo"
      >
        <div className="border border-white/10 bg-white/[0.02] px-4 py-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-white/75">{series.team1}</span>
            <span className="font-mono text-2xl tracking-tight text-white">{series.score1}</span>
          </div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-sm text-white/45">{series.team2}</span>
            <span className="font-mono text-2xl tracking-tight text-white/45">
              {series.score2}
            </span>
          </div>
        </div>
        <div className="mt-4 space-y-1.5">
          {series.maps.map((map) => (
            <div key={map.map} className="flex items-center justify-between gap-3 text-[12px]">
              <span className="w-16 text-white/65">{map.map}</span>
              <span
                className={`font-mono ${
                  map.score1 > map.score2 ? 'text-white/70' : 'text-white/35'
                }`}
              >
                {map.score1}–{map.score2}
              </span>
              <span className="w-14 text-right text-white/25">{map.pickedBy}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3 font-mono text-[12px] text-white/35">
          <span>{series.maps.length} maps</span>
          <span>{series.rounds} rounds</span>
          <span>{series.vods} VODs</span>
        </div>
      </PreviewShell>
    );
  }

  if (id === 'event') {
    const event = snapshot.event;

    return (
      <PreviewShell
        eyebrow="Event overview"
        title={event.name}
        meta={`${event.country} · ${dateRange(event.startDate, event.endDate)}`}
        badge="EventStandings"
      >
        <div className="space-y-1.5">
          {event.stages.map((stage) => (
            <div
              key={stage.name}
              className="flex items-center justify-between border border-white/[0.07] bg-white/[0.02] px-3 py-2"
            >
              <span className="text-[12px] text-white/65">{stage.name}</span>
              <span className="font-mono text-[12px] text-white/30">
                {dateRange(stage.startDate, stage.endDate)}
              </span>
            </div>
          ))}
        </div>
        <div className="mt-4 border-t border-white/10 pt-3">
          <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-white/30">
            Playoffs standings
          </p>
          <div className="mt-2 space-y-1.5">
            {event.standings.map((row) => (
              <div key={row.team} className="flex items-center gap-3 text-[12px]">
                <span className="w-7 font-mono text-white/35">{row.place}</span>
                <span className="truncate text-white/65">{row.team}</span>
                <span className="ml-auto font-mono text-[12px] text-white/25">
                  {row.points} pts
                </span>
              </div>
            ))}
          </div>
        </div>
      </PreviewShell>
    );
  }

  const news = snapshot.news;

  return (
    <PreviewShell
      eyebrow="News article"
      title={news.title}
      meta={`By ${news.author} · ${shortDateFromIso(news.date)}`}
      badge="NewsArticle"
    >
      <p className="text-[12px] leading-relaxed text-white/50">{news.subtitle}</p>
      <div className="mt-3 border border-white/10 bg-white/[0.02] p-3.5">
        <p className="font-mono text-[12px] text-white/30">content_md</p>
        <p className="mt-2 text-[12px] leading-relaxed text-white/55 [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:4] overflow-hidden">
          {news.excerpt}
        </p>
      </div>
      <div className="mt-3 flex items-center justify-between font-mono text-[12px] text-white/30">
        <span>{news.country}</span>
        <span>{news.links} links · Markdown preserved</span>
      </div>
    </PreviewShell>
  );
}

function CodePanel({ module }: { module: (typeof modules)[number] }) {
  return (
    <div className="flex h-full min-w-0 flex-col overflow-hidden border border-white/10 bg-[#070707]">
      <div className="flex items-center justify-between gap-3 border-b border-white/10 px-3.5 py-2.5">
        <div className="flex items-center gap-2">
          <span aria-hidden="true" className="size-1.5 bg-[#ff4655]" />
          <span className="font-mono text-[12px] text-white/40">{module.file}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="hidden font-mono text-[12px] uppercase tracking-[0.12em] text-white/25 sm:inline">
            {displayModelName(module.returns)}
          </span>
          <CopyButton value={module.code} label={`Copy ${module.file}`} />
        </div>
      </div>
      <div className="flex-1 overflow-auto">
        <CodeBlock code={module.code} />
      </div>
      <div className="flex flex-wrap gap-1.5 border-t border-white/10 bg-white/[0.02] px-3.5 py-3">
        {module.methods.map((method) => (
          <code
            key={method}
            className="border border-white/10 px-1.5 py-0.5 font-mono text-[12px] text-white/40"
          >
            {method}
          </code>
        ))}
      </div>
    </div>
  );
}

export function ModuleShowcase() {
  const [activeId, setActiveId] = useState<ModuleId>('player');

  useEffect(() => {
    const sections = modules
      .map((module) => document.getElementById(module.id))
      .filter((section): section is HTMLElement => section !== null);

    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) setActiveId(visible[0].target.id as ModuleId);
      },
      { rootMargin: '-18% 0px -58% 0px', threshold: [0, 0.15, 0.4] },
    );

    for (const section of sections) observer.observe(section);
    return () => observer.disconnect();
  }, []);

  function scrollToModule(event: MouseEvent<HTMLAnchorElement>, id: ModuleId) {
    event.preventDefault();
    setActiveId(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    window.history.replaceState(null, '', `#${id}`);
  }

  return (
    <div className="grid min-w-0 grid-cols-1 gap-10 lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-14 xl:grid-cols-[280px_minmax(0,1fr)] xl:gap-16">
      <div className="min-w-0 lg:sticky lg:top-24 lg:self-start">
        <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-white/35">
          The namespaces
        </p>
        <h2 className="mt-4 text-2xl font-medium leading-[1.06] tracking-[-0.03em] text-white sm:text-3xl">
          Every surface.
          <br />
          <span className="text-white/35">One import.</span>
        </h2>
        <p className="mt-4 max-w-sm text-[13px] leading-relaxed text-white/40">
          Bind an ID once, then query everything attached to it. Scroll through the full surface,
          or jump straight to a namespace.
        </p>

        <nav aria-label="API namespaces" className="mt-7 border-t border-white/10">
          {modules.map((module, index) => {
            const active = module.id === activeId;
            return (
              <a
                key={module.id}
                href={`#${module.id}`}
                onClick={(event) => scrollToModule(event, module.id)}
                aria-current={active ? 'true' : undefined}
                className={`group flex items-center gap-3 border-b border-white/10 py-3.5 text-[13px] transition-colors ${
                  active ? 'text-white' : 'text-white/40 hover:text-white/75'
                }`}
              >
                <span
                  aria-hidden="true"
                  className={`h-4 w-px transition-colors duration-300 ${
                    active ? 'bg-[#ff4655]' : 'bg-white/10'
                  }`}
                />
                <span className="font-mono text-[12px] text-white/25">
                  0{index + 1}
                </span>
                <span className="font-medium">{module.label}</span>
                <span
                  aria-hidden="true"
                  className={`ml-auto size-1 transition-all duration-300 ${
                    active ? 'bg-[#ff4655] opacity-100' : 'bg-transparent opacity-0'
                  }`}
                />
              </a>
            );
          })}
        </nav>

        <Link
          href="/docs/reference/"
          className="group mt-6 inline-flex items-center gap-1.5 text-[12px] font-medium text-white/40 transition-colors hover:text-white"
        >
          Browse the full reference
          <ArrowUpRight
            className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      </div>

      <div className="min-w-0 space-y-10 sm:space-y-14">
        {modules.map((module, index) => (
          <Reveal key={module.id}>
            <section id={module.id} data-module={module.id} className="min-w-0 scroll-mt-24">
              <div className="flex flex-wrap items-end justify-between gap-3 border-b border-white/10 pb-4">
                <div className="flex items-start gap-3">
                  <span className="mt-1 font-mono text-[12px] text-[#ff4655]">
                    0{index + 1}
                  </span>
                  <div>
                    <h3 className="text-xl font-medium tracking-tight text-white">{module.label}</h3>
                    <p className="mt-1 max-w-lg text-[13px] leading-relaxed text-white/40">
                      {module.blurb}
                    </p>
                  </div>
                </div>
                <Link
                  href={module.href}
                  className="group inline-flex items-center gap-1 pb-0.5 font-mono text-[12px] uppercase tracking-[0.12em] text-white/30 transition-colors hover:text-white/70"
                >
                  {displayModelName(module.returns)}
                  <ArrowUpRight
                    className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                    aria-hidden="true"
                  />
                </Link>
              </div>

              <div className="mt-4 grid min-w-0 grid-cols-1 items-stretch gap-3 xl:grid-cols-[1.12fr_0.88fr]">
                <CodePanel module={module} />
                <div className="min-w-0 border border-white/10 bg-[#080808]">
                  <Preview id={module.id} />
                </div>
              </div>
            </section>
          </Reveal>
        ))}
      </div>
    </div>
  );
}
