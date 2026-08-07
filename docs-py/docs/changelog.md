# Changelog

All notable changes to this project will be documented in this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
