# Changelog

All notable changes to this project will be documented in this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.3.0] - 2026-08-11

### Added

- **News namespace** — `vlrdevapi.news(page=1)` lists news items from
  vlr.gg/news, each with `title`, `subtitle`, `link`, `country_name`,
  `date`, and `author`, plus `has_next_page` and `page_number` on the
  returned page.
- **News article content** — `vlrdevapi.news.article(article_id)` fetches
  a single news article with its `title`, `author`, `date`, associated
  `event_name`/`event_link`, and the full `content` body text. The body
  is also available as Markdown via `content_md`, preserving headings,
  lists, links, emphasis, and clip embeds.
- **News out-of-range pages** — requesting a news page beyond the last
  available page now raises `NotFoundError` instead of silently returning
  an empty result.

### Changed

- **News article Markdown links are absolute** — links in `content_md` are
  prefixed with `https://www.vlr.gg` when they were relative (e.g.
  `/player/5132/mada` → `https://www.vlr.gg/player/5132/mada`). Absolute
  and `www.`-prefixed URLs are left untouched. `NewsArticle.event_link` is
  now an absolute URL as well.

### Fixed

- **News article clip embeds** — `content_md` clip embeds now link to the
  directly openable watch URL (e.g. `https://clips.twitch.tv/<slug>`) for
  Twitch clips, Twitch VODs, YouTube, and Soop embeds, instead of the embed
  URL which could not be opened in a new tab.
- **News article Markdown whitespace/emphasis** — inline emphasis and bold
  render correctly around links: source indentation whitespace no longer
  produces double spaces, and `*`/`**` markers no longer wrap whitespace.
- **News article dates are timezone-aware** — the article date is parsed
  through the shared `commons.parse_vlr_iso_datetime` helper. Offset-aware
  `datetime` attributes are converted to UTC as-is; naive values are
  localised to the client's `source_tz` (or UTC) instead of the local
  machine timezone.
- **Unknown article IDs raise `NotFoundError`** — vlr.gg returns a generic
  HTTP 200 page for non-existent article IDs; `news.article()` now detects
  the missing article card and raises `NotFoundError` instead of returning
  an empty article.
- **News article Markdown fidelity** — `content_md` now renders nested
  lists, tables (as pipe tables), and inline `code` verbatim (whitespace
  preserved). Links whose href is `www.`-prefixed are upgraded to
  `https://`, fixing broken relative links in Markdown.
- **Documentation** — news reference pages updated (article, list, index),
  plus the getting-started guide, main docs index, and README now cover the
  news namespace; model/parser docstrings describe the current behaviour.

## [2.2.0] - 2026-08-11

### Changed

- **Events list dates without a year** — `event.list()` dates are rendered
  on vlr.gg without a year (e.g. `"Jul 9 - Aug 23"`). These now use a
  sentinel year of `2019` instead of the current year. Any parsed date with
  `year < 2020` means the source omitted the year, so guard with
  `event.start_date.year < 2020` before relying on it.
- **Series performance field renames (breaking)** — `AdvStatsEntry` fields
  were renamed to descriptive names: `econ` → `economy`, `pl` → `plants`,
  and `de` → `defuses`. Update any code referencing the old field names.
  The series performance reference docs were updated to match.

### Fixed

- **Python 3.13/3.15 date parsing deprecation** — `datetime.strptime` emits
  a `DeprecationWarning` when parsing a day-of-month without a year (and will
  change behavior in Python 3.15). All such parses now supply an explicit
  year derived from context (reference date, page-header year, or the
  sentinel above).
- **Series per-game stats by game number** — `players()`, `rounds()`,
  `performance()`, and `economy()` game identifiers can now be a 1-based
  game number within the series, resolved to the real VLR game ID from the
  page's game nav tabs. A real VLR game ID is still accepted unchanged;
  previously passing a game number produced empty results.
- **Series economy and rounds scope** — economy and round-by-round data are
  now parsed from the selected game's section only. The economy parser
  previously collected tables from the whole page, so a per-game request
  could include data from other maps.
- **Series performance player IDs** — the performance tab renders player
  cells without links, leaving player IDs as `0`. IDs are now recovered from
  the series overview tab (keyed by team abbreviation and player name) and
  attached to kill-matrix entries, advanced stats, and notable-round victims.

## [2.1.0] - 2026-08-07

### Added

- **Event teams player rosters** — `event.teams()` now includes a `players`
  list on each `Team`, containing each player's `name` and `id` parsed from
  the event page. The `players` field is always present and defaults to `[]`
  when roster data is unavailable. A new `TeamPlayer` model was added and exposed
  from the `_event.teams` submodule.

### Changed

- **Documentation** — event teams reference updated with the new `players`
  field, a `TeamPlayer` fields table, and a roster iteration example.

## [2.0.1] - 2026-07-29

### Fixed

- **Series player stats** — overview tab HTML changed from `<table>` to
  `<div>` on vlr.gg; updated CSS selectors to match the new structure.
- **Player agent stats** — agent table class changed from `wf-table` to
  `st-table.mod-agent-rows`; column count reduced from 17 to 16 (FKPR and
  FDPR columns consolidated into a single FK:FD ratio column).
- **Player profile** — same agent table selector fix; the profile fallback
  to `timespan=all` now works correctly.
- **Team fixtures** — updated stale test assertions for NRG Haven map
  stats (games played, wins, losses, etc.) and total winnings to match
  current vlr.gg data.

### Removed

- `fkpr` and `fdpr` fields from `AgentStats` model — vlr.gg no longer
  exposes separate First Kills Per Round / First Deaths Per Round columns.
  The `first_kills` and `first_deaths` total fields remain available.

### Changed

- **Documentation** — agents schema reference updated to reflect the
  removal of `fkpr` and `fdpr`.

## [2.0.0] - 2026-07-07

### Major Rewrite

Complete rewrite of the library. v2.0.0 replaces the asynchronous
aiohttp-based v1.x with a synchronous httpx-based architecture.
The API surface, module structure, and type system are all new.

### Added

- **Sync-first client** — `VLRClient` with context manager support and
  thread-safe parallel enrichment for bulk operations.
- **Curried access pattern** — bind a player/team/series/event ID once,
  then chain sub-methods without re-passing the ID.
- **Event namespace** — list with pagination and filtering (tier, region,
  status), plus info, matches, stages, standings, and teams.
- **Match listing namespace** — live, upcoming (paginated), and completed
  (paginated) match feeds with team enrichment.
- **Player namespace** — info, teams (current/past), agent stats
  (30d/60d/90d/all), match history (paginated), and consolidated profile.
- **Series namespace** — info (veto, games, scores), player stats per game,
  round-by-round data, performance (kill matrices, advanced stats),
  economy (buy types, spend analysis), and VOD links.
- **Team namespace** — info, roster, stats (per-map with optional agent
  composition), placements, transactions, completed and upcoming matches.
- **Pydantic v2 models** — fully typed with Google-style docstrings and
  field descriptions.
- **Built-in resilience** — configurable retry with exponential/linear/
  constant backoff, jitter, and token-bucket rate limiting.
- **Thread-safe LRU cache** — bounded `LRUCache` for team data to avoid
  redundant HTTP requests during enrichment.
- **Input validation** — `@sanitize_and_validate` decorator with positive-ID
  checks and Pydantic type coercion.
- **Custom exceptions** — typed hierarchy (`NotFoundError`, `RateLimitError`,
  `ParsingError`, `ValidationError`, etc.) for clean error handling.
- **Documentation** — Zensical/MkDocs site via `docs-py/` (ReadTheDocs)
  with auto-generated API reference from docstrings.
- **Official website** — Next.js + Fumadocs site via `official-docs/`
  (Cloudflare Pages) with interactive code examples.
- **Doc validation** — `scripts/check_mdx_examples.py` validates syntax,
  imports, and live execution of all code examples in docs.

### Changed

- **Architecture** — migrated from async aiohttp to synchronous httpx.
  No more `await` or `async with` required.
- **No explicit session management** — `VLRClient` handles connection
  pooling, retries, and rate limiting internally.
- **Type system** — replaced raw dict returns with Pydantic v2 models
  for all endpoints.
- **Build system** — moved from setuptools to hatchling with `uv` for
  dependency management.
- **Python requirement** — raised minimum to 3.11.

### Removed

- All v1.x async endpoints (`get_event`, `get_team`, `get_player`, etc.)
  are removed. See the new module-level or client-based API.
- `aiohttp` and `asyncio` dependencies.
- v1.x match/event/team parsing modules.
