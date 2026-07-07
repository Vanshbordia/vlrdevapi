# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-07-07

### Major Rewrite

Complete rewrite of the library. v2.0.0 replaces the asynchronous
aiohttp-based v1.x with a synchronous httpx-based architecture.
The API surface, module structure, and type system are all new.

### Added

- **Sync-first client** - `VLRClient` with context manager support and
  thread-safe parallel enrichment for bulk operations.
- **Curried access pattern** - bind a player/team/series/event ID once,
  then chain sub-methods without re-passing the ID.
- **Event namespace** - list with pagination and filtering (tier, region,
  status), plus info, matches, stages, standings, and teams.
- **Match listing namespace** - live, upcoming (paginated), and completed
  (paginated) match feeds with team enrichment.
- **Player namespace** - info, teams (current/past), agent stats
  (30d/60d/90d/all), match history (paginated), and consolidated profile.
- **Series namespace** - info (veto, games, scores), player stats per game,
  round-by-round data, performance (kill matrices, advanced stats),
  economy (buy types, spend analysis), and VOD links.
- **Team namespace** - info, roster, stats (per-map with optional agent
  composition), placements, transactions, completed and upcoming matches.
- **Pydantic v2 models** - fully typed with Google-style docstrings and
  field descriptions.
- **Built-in resilience** - configurable retry with exponential/linear/
  constant backoff, jitter, and token-bucket rate limiting.
- **Thread-safe LRU cache** - bounded `LRUCache` for team data to avoid
  redundant HTTP requests during enrichment.
- **Input validation** - `@sanitize_and_validate` decorator with positive-ID
  checks and Pydantic type coercion.
- **Custom exceptions** - typed hierarchy (`NotFoundError`, `RateLimitError`,
  `ParsingError`, `ValidationError`, etc.) for clean error handling.
- **Documentation** - Zensical/MkDocs site via `docs-py/` (ReadTheDocs)
  with auto-generated API reference from docstrings.
- **Official website** - Next.js + Fumadocs site via `official-docs/`
  (Cloudflare Pages) with interactive code examples.
- **Doc validation** - `scripts/check_mdx_examples.py` validates syntax,
  imports, and live execution of all code examples in docs.

### Changed

- **Architecture** - migrated from async aiohttp to synchronous httpx.
  No more `await` or `async with` required.
- **No explicit session management** - `VLRClient` handles connection
  pooling, retries, and rate limiting internally.
- **Type system** - replaced raw dict returns with Pydantic v2 models
  for all endpoints.
- **Build system** - moved from setuptools to hatchling with `uv` for
  dependency management.
- **Python requirement** - raised minimum to 3.11.

### Removed

- All v1.x async endpoints (`get_event`, `get_team`, `get_player`, etc.)
  are removed. See the new module-level or client-based API.
- `aiohttp` and `asyncio` dependencies.
- v1.x match/event/team parsing modules.

[2.0.0]: https://github.com/Vanshbordia/vlrdevapi/compare/v1.6.2...v2.0.0
