import type { Metadata } from 'next'

import ChangelogTimeline from './changelog-timeline'

export const metadata: Metadata = {
  title: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
}

const versions = [
  {
    version: '2.4.0',
    date: '19 August 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.4.0',
    pypi: 'https://pypi.org/project/vlrdevapi/2.4.0/',
    summary: 'Adds Bo1 series support, event subregion resolution, a shared commons.regions module, series forfeit detection, and fixes economy/rounds enrichment mismatches.',
    sections: [
      {
        title: 'Added',
        items: [
          'Bo1 series support — single-map series now resolve games from `.vm-stats-game` containers when nav tabs are absent. `resolve_game_id` raises `ParsingError` instead of silently returning wrong data.',
          'Event region resolution — `_parse_breadcrumb` resolves `subregion=` breadcrumb links (e.g. "Japan", "North America") to their parent region via `commons.regions.resolve_subregion_to_region`. New `EventRegion.subregion` field preserves the original subregion name.',
          'Event country-to-region fallback — when no breadcrumb region is present, the `region_location` country flag is resolved via `resolve_country_to_region` to infer the parent region.',
          'Event region deduplication — duplicate region entries (from both `region=` and `subregion=` breadcrumbs for the same parent) are collapsed, preferring the entry that carries a subregion name.',
          'New `commons.regions` module with `VALID_REGIONS`, `SUBREGION_TO_REGION` (17 VCL/GC subregions), `COUNTRY_TO_REGION` (~100+ countries), `resolve_subregion_to_region`, and `resolve_country_to_region`.',
          'Region utilities re-exported from `vlrdevapi.commons` for convenience.',
          'Series forfeit detection — new `ForfeitInfo` model on `SeriesInfo.forfeit` exposes `forfeited`, `team`, `team_id`, and `reason` fields. Parser detects "forfeited by TEAM" in the match header and maps the team name to the corresponding team ID.',
          'Series match notes — new `SeriesInfo.notes` list captures non-veto `match-header-note` text such as technical pause warnings and lobby remake notices.',
        ],
      },
      {
        title: 'Changed',
        items: [
          'Series economy and rounds enrichment now try abbreviation-level names from `.ovw-player-tag` elements first (e.g. "SEN"), then fall back to full team names. This fixes mismatches where the economy/rounds tab shows a different abbreviation than the overview header.',
          'Bo1 veto fallback now handles the "bans + decider" pattern (e.g. "Ban1 remains") in addition to pick/ban. The PICK badge is excluded from map names.',
          'Series info notes parsing now iterates all `match-header-note` elements instead of only the first, correctly separating forfeit reasons, informational notes, and map veto text.',
        ],
      },
      {
        title: 'Fixed',
        items: [
          'Economy bank/spend parsing — `int()` calls on `.rnd-sq` title attributes and `.rnd-num` text are wrapped in `try/except ValueError`; malformed values default to `0` instead of crashing the parser.',
          'Event region from location country — events that only have a "Location" label with a flag (no separate "Region" label) now resolve the region from `location.country` via `resolve_country_to_region`.',
          'Phantom pagination in matches — terminal pages no longer report `has_next_page = True` (PR #50).',
        ],
      },
      {
        title: 'Documentation',
        items: [
          'Event info reference — `EventRegion` fields table now documents the `subregion` field. Region example demonstrates subregion access.',
          'Series info reference — `ForfeitInfo` fields table documents the new `forfeit` nested model. `notes` field description explains the distinction between forfeit reasons and informational notes.',
          'Series economy/rounds docstrings reference correct model types.',
          'Project structure in contributing guide updated with actual directory names and new modules.',
        ],
      },
    ],
  },
  {
    version: '2.3.0',
    date: '11 August 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.3.0',
    pypi: 'https://pypi.org/project/vlrdevapi/2.3.0/',
    summary: 'Adds a news namespace for browsing vlr.gg news listings and fetching full article content.',
    sections: [
      {
        title: 'Added',
        items: [
          '`vlrdevapi.news(page=1)` lists news items from vlr.gg/news, each with `title`, `subtitle`, `link`, `country_name`, `date`, and `author`, plus `has_next_page` and `page_number` on the returned page.',
          '`vlrdevapi.news.article(article_id)` fetches a single news article with its `title`, `author`, `date`, associated `event_name`/`event_link`, and the full `content` body text. The body is also available as Markdown via `content_md`, preserving headings, lists, links, emphasis, and clip embeds.',
          'Requesting a news page beyond the last available page (e.g. `page=176`) now raises `NotFoundError` instead of silently returning an empty result.',
        ],
      },
      {
        title: 'Changed',
        items: [
          'News article Markdown links are now absolute: links in `content_md` are prefixed with `https://www.vlr.gg` when they are relative (e.g. `/player/5132/mada` → `https://www.vlr.gg/player/5132/mada`). Absolute and `www.`-prefixed URLs are left untouched. `NewsArticle.event_link` is now an absolute URL as well.',
        ],
      },
      {
        title: 'Fixed',
        items: [
          'News article clip embeds — `content_md` clip embeds now link to the directly openable watch URL (e.g. `https://clips.twitch.tv/<slug>`) for Twitch clips, Twitch VODs, YouTube, and Soop embeds, instead of the embed URL which could not be opened in a new tab.',
          'News article Markdown whitespace/emphasis — inline emphasis and bold render correctly around links: source indentation whitespace no longer produces double spaces, and `*`/`**` markers no longer wrap whitespace.',
          'News article dates are now timezone-aware — the article date is parsed through the shared `parse_vlr_iso_datetime` helper. Offset-aware `datetime` attributes are converted to UTC as-is; naive values are localised to the client\'s `source_tz` (or UTC) instead of the local machine timezone.',
          'Unknown article IDs now raise `NotFoundError` — vlr.gg returns a generic HTTP 200 page for non-existent article IDs; `news.article()` detects the missing article card and raises `NotFoundError` instead of returning an empty article.',
          'News article Markdown fidelity — `content_md` now renders nested lists, tables (as pipe tables), and inline `code` verbatim (whitespace preserved). Links whose href is `www.`-prefixed are upgraded to `https://`, fixing broken relative links in Markdown.',
        ],
      },
    ],
  },
  {
    version: '2.2.0',
    date: '11 August 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.2.0',
    pypi: 'https://pypi.org/project/vlrdevapi/2.2.0/',
    summary: 'Renames series performance fields, fixes per-game series stat resolution, and uses a sentinel year for events-list dates that omit the year.',
    sections: [
      {
        title: 'Changed',
        items: [
          '`event.list()` dates are rendered on vlr.gg without a year (e.g. "Jul 9 – Aug 23"). These now use a sentinel year of `2019` instead of the current year. Any parsed date with `year < 2020` means the source omitted the year, so guard with `event.start_date.year < 2020` before relying on it.',
          '`AdvStatsEntry` fields renamed to descriptive names: `econ` → `economy`, `pl` → `plants`, and `de` → `defuses`. Update any code referencing the old field names. The series performance reference docs were updated to match.',
        ],
      },
      {
        title: 'Fixed',
        items: [
          '`datetime.strptime` emits a `DeprecationWarning` when parsing a day-of-month without a year (and will change behavior in Python 3.15). All such parses now supply an explicit year derived from context (reference date, page-header year, or the sentinel above).',
          'Series `players()`, `rounds()`, `performance()`, and `economy()` game identifiers can now be a 1-based game number within the series, resolved to the real VLR game ID from the page\'s game nav tabs. A real VLR game ID is still accepted unchanged; previously passing a game number produced empty results.',
          'Series economy and round-by-round data are now parsed from the selected game\'s section only. The economy parser previously collected tables from the whole page, so a per-game request could include data from other maps.',
          'Series performance player IDs are now recovered from the series overview tab (keyed by team abbreviation and player name) and attached to kill-matrix entries, advanced stats, and notable-round victims, instead of being left as `0`.',
        ],
      },
    ],
  },
  {
    version: '2.1.0',
    date: '7 August 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.1.0',
    pypi: 'https://pypi.org/project/vlrdevapi/2.1.0/',
    summary: 'Adds player rosters to event teams, exposing each player\'s name and id on every team.',
    sections: [
      {
        title: 'Added',
        items: [
          '`event.teams()` now includes a `players` list on each `Team`, containing each player\'s `name` and `id` parsed from the event page.',
          'New `TeamPlayer` model exposed from the `_event.teams` submodule.',
          'The `players` field is always present and defaults to `[]` when roster data is unavailable.',
        ],
      },
      {
        title: 'Changed',
        items: [
          'Event teams reference docs updated with the new `players` field, a `TeamPlayer` fields table, and a roster iteration example.',
        ],
      },
    ],
  },
  {
    version: '2.0.1',
    date: '29 July 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.0.1',
    pypi: 'https://pypi.org/project/vlrdevapi/2.0.1/',
    summary: 'Maintenance release removing deprecated agent stat fields removed by vlr.gg and updating CSS selectors for the latest site markup.',
    sections: [
      {
        title: 'Changed',
        items: [
          'Agents schema reference updated to reflect the removal of `fkpr` and `fdpr`.',
        ],
      },
      {
        title: 'Fixed',
        items: [
          'Series player stats — the overview tab HTML changed from `<table>` to `<div>` on vlr.gg; CSS selectors updated to match the new structure.',
          'Player agent stats — the agent table class changed from `wf-table` to `st-table.mod-agent-rows`, and the column count dropped from 17 to 16 after FKPR and FDPR merged into a single FK:FD ratio column.',
          'Player profile — same agent table selector fix; the fallback to `timespan=all` now works correctly.',
          'Team fixtures — stale test assertions updated for NRG Haven map stats and total winnings to match current vlr.gg data.',
        ],
      },
      {
        title: 'Removed',
        items: [
          '`fkpr` and `fdpr` fields from `AgentStats` — vlr.gg consolidated the separate "First Kills Per Round" and "First Deaths Per Round" columns into a single "FK:FD" ratio. Use the existing `first_kills` and `first_deaths` total fields instead.',
        ],
      },
    ],
  },
  {
    version: '2.0.0',
    date: '7 July 2026',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.0.0',
    pypi: 'https://pypi.org/project/vlrdevapi/2.0.0/',
    summary: 'Complete rewrite of the library. v2.0.0 replaces the asynchronous aiohttp-based v1.x with a synchronous httpx-based architecture.',
    sections: [
      {
        title: 'Added',
        items: [
          'Synchronous `VLRClient` with context manager support and thread-safe parallel enrichment for bulk operations.',
          'Curried access pattern — bind a player/team/series/event ID once, then chain sub-methods without re-passing the ID.',
          'Event namespace — list with pagination and filtering (tier, region, status), plus info, matches, stages, standings, and teams.',
          'Match listing namespace — live, upcoming (paginated), and completed (paginated) match feeds with team enrichment.',
          'Player namespace — info, teams (current/past), agent stats (`30d`/`60d`/`90d`/`all`), match history (paginated), and consolidated profile.',
          'Series namespace — info (veto, games, scores), player stats per game, round-by-round data, performance (kill matrices, advanced stats), economy (buy types, spend analysis), and VOD links.',
          'Team namespace — info, roster, stats (per-map with optional agent composition), placements, transactions, and completed/upcoming matches.',
          'Pydantic v2 models — fully typed with Google-style docstrings and field descriptions.',
          'Built-in resilience — configurable retry with exponential/linear/constant backoff, jitter, and token-bucket rate limiting.',
          'Thread-safe LRU cache — bounded `LRUCache` to avoid redundant HTTP requests during enrichment.',
          'Input validation — `@sanitize_and_validate` decorator with positive-ID checks and Pydantic type coercion.',
          'Custom exceptions — typed hierarchy (`NotFoundError`, `RateLimitError`, `ParsingError`, `ValidationError`, etc.).',
          'Module-level convenience access via `import vlrdevapi` with a lazy-initialized default client.',
          'Official website and API reference built with Next.js + Fumadocs and Zensical/MkDocs, with live doc validation in CI.',
          'Comprehensive test suite with fixture-based offline tests and live integration tests.',
        ],
      },
      {
        title: 'Changed',
        items: [
          'Architecture — migrated from async aiohttp to synchronous httpx. No more `await` or `async with` required.',
          'No explicit session management — `VLRClient` handles connection pooling, retries, and rate limiting internally.',
          'Type system — replaced raw dict returns with Pydantic v2 models for all endpoints.',
          'Build system — moved from setuptools to hatchling with `uv` for dependency management.',
          'Python requirement — raised minimum to 3.11.',
        ],
      },
      {
        title: 'Removed',
        items: [
          'All v1.x async endpoints (`get_event`, `get_team`, `get_player`, etc.) — see the new module-level or client-based API.',
          '`aiohttp` and `asyncio` dependencies.',
          'v1.x match/event/team parsing modules.',
        ],
      },
    ],
  },
]

const jsonLdBreadcrumb = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://vlrdevapi.pages.dev' },
    { '@type': 'ListItem', position: 2, name: 'Changelog', item: 'https://vlrdevapi.pages.dev/changelog/' },
  ],
}

const jsonLdWebPage = {
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  name: 'Changelog',
  description: 'Release history and version notes for VLRdevAPI.',
  url: 'https://vlrdevapi.pages.dev/changelog/',
  about: {
    '@type': 'SoftwareSourceCode',
    name: 'VLRdevAPI',
    programmingLanguage: 'Python',
    runtimePlatform: 'Python 3.11+',
    codeRepository: 'https://github.com/vanshbordia/vlrdevapi',
    author: [
      {
        '@type': 'Person',
        name: 'Vansh Bordia',
      },
      {
        '@type': 'Organization',
        name: 'RiftWatch',
        url: 'https://riftwatch.org',
      },
    ],
  },
}

export default function ChangelogPage() {
  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdBreadcrumb).replace(/</g, '\\u003c'),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLdWebPage).replace(/</g, '\\u003c'),
        }}
      />
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 pt-28 pb-16 md:pt-36 md:pb-20">
          <h1 className="font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem]">
            Changelog
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            Track every release, feature, and fix in VLRdevAPI.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <ChangelogTimeline versions={versions} />
        </div>
      </section>
    </main>
  )
}
