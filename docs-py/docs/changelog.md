# Changelog

All notable changes to this project will be documented in this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [3.1.0] - 2026-10-25

### Added

- **Multi-Format Tabular Export Layer** — All Pydantic models now inherit from `ExportableModel`, enabling seamless tabular serialization into popular data science formats:
  - `.to_records()` — extracts clean, unnested lists of Python dictionaries with semantic flattening across every namespace.
  - `.to_df()` — converts records directly into a `pandas.DataFrame`.
  - `.to_polars()` — converts records directly into a native `polars.DataFrame` with typed nested arrays (`pl.List(pl.String)`).
  - `.to_csv(path=None)` — exports to standard CSV format with semicolon-delimited lists (`"Player;IGL"`) and in-memory string output when `path` is omitted.
  - `.to_parquet(path, index=False)` — writes Apache Parquet files via pandas and pyarrow.
  - `.to_excel(path, sheet_name="Sheet1", index=False)` — exports Excel `.xlsx` spreadsheets via pandas and openpyxl.
  - `.to_json(path=None, indent=2)` — exports clean serialized JSON to string or disk with comprehensive recursive datetime and list handling.
  - `.to_markdown(columns=None)` — generates GitHub-flavored markdown tables with proper column alignments, pipe escaping, and zero dependencies.
- **Granular Optional Dependency Extras** — Data export dependencies are strictly optional and modular:
  - `vlrdevapi[pandas]`: installs `pandas>=2.0.0`
  - `vlrdevapi[polars]`: installs `polars>=1.0.0`
  - `vlrdevapi[excel]`: installs `openpyxl>=3.1.0` and `pandas>=2.0.0`
  - `vlrdevapi[parquet]`: installs `pyarrow>=14.0.0` and `pandas>=2.0.0`
  - `vlrdevapi[mcp]`: installs `mcp>=1.2.0`
  - `vlrdevapi[all]`: installs all optional tabular, file, and MCP dependencies.
  - Missing dependencies provide actionable, friendly install prompts with exact pip commands instead of generic import errors.
- **First-Class Model Context Protocol (MCP) Server** — Built-in MCP server for AI agents and LLMs (Claude Desktop, Cursor, Zed, Antigravity):
  - CLI executable `vlrdevapi-mcp` (or `python -m vlrdevapi.mcp.server`, `uvx vlrdevapi-mcp`).
  - Standard `stdio` transport with structured, formatted tool definitions.
  - 40 tools covering all endpoints across Matches, Series, Teams, Players, Events, and News.
  - High-level composite tools for complex agent tasks:
    - `get_match_full_context(series_id)` — aggregates overview, player statistics, and streams/VODs into a single response.
    - `get_team_overview(team_id)` — combines team info, roster, upcoming schedule, and tournament placements.
    - `compare_teams(team_id_1, team_id_2, last_days=60)` — side-by-side comparison of two teams with rosters and recent map statistics/forms.
    - `get_player_career_summary(player_id)` — consolidated dossier with profile, current teams, agent pool ratings, and tournament placements.
    - `get_h2h_matchup(team_id_1, team_id_2)` — head-to-head match history between two organizations.
    - `get_tournament_dossier(event_id)` — tournament overview with participating teams, stages, and standings.
    - `get_live_and_upcoming_schedule(limit)` — live ticker combined with upcoming match schedule.
    - `get_news_digest(limit, include_top_article_body)` — latest esports headlines with optional top article body.
    - `series_map_summary(series_id, game_id)` — targeted map-level overview combining economy, replay timeline, and player stats.
- **Python 3.15 Ready** — Added Python 3.15 to the CI/CD test and publish workflows, verified across uv python matrix.
- **Production/Stable Status** — Package status promoted to `Development Status :: 5 - Production/Stable` in package metadata.

### Improved

- **Semantic Model Flattening** — Tabular export extractors (`.to_records()`) now generate clean, non-redundant rows:
  - Upcoming/completed matches omit static status columns and resolve unannounced teams as `"TBD"`.
  - Player agent statistics provide unnested, clean numeric columns (`acs`, `kd`, `adr`, `kast`, `kpr`, `apr`).
  - Series player stats properly segregate map rows, labeling the aggregate map view as `"All Maps"`.
  - Team rosters separate `primary_role` and multi-role lists.
- **Unified Serialization in MCP Tools** — MCP server tools now leverage `ExportableModel.to_dict()` and `ExportableModel.to_json()`, eliminating redundant ad-hoc JSON conversion and drastically speeding up tool invocations.
- **CSV Multi-Value List Formatting** — Agent lists and team roles are formatted with standard semicolon delimiters (`"neon;raze;jett"`) instead of Python `repr()` strings, ensuring full compatibility with spreadsheet applications and analytical parsers.
- **Parser Corrections** — Fixed swapped KAST and ADR columns in `player.agents()` table extraction to match VLR.gg's actual table headers.

## [3.0.0] - 2026-10-23

### Breaking

- **`BuyType` re-tiered to match vlr.gg** — the economy tab no longer uses
  its old four spend tiers. `SEMI_ECO` and `SEMI_BUY` are removed and the
  remaining tiers follow VLR's current categories based on total team
  spend: `ECO` (under 10k), `HALF_BUY` (10k–18k), and `FULL_BUY` (18k+).
  A new `PISTOL` member marks pistol-round buys (previously reported as
  `ECO`). Code switching on `BuyType.SEMI_ECO` / `BuyType.SEMI_BUY` needs
  updating; string values are `"Pistol"`, `"Eco"`, `"Half-buy"`,
  `"Full-buy"`.

### Added

- **Buy-type matrix** — `EconomyData` now carries the economy tab's
  buy-type matrix as `buy_matrix_team1` / `buy_matrix_team2`
  (`TeamBuyMatrix`): the Pistol / Conv. / Bonus summary and the
  `On Eco` / `On Half buy` / `On Full buy` records
  (`BuyTierRecord.vs_eco` / `vs_half` / `vs_full`), each a
  `won`/`total` `EconScore`. Unplayed matchups are `None`.
  `series.economy(game_id="all")` on the parser also now returns the
  all-maps aggregate matrix instead of an empty result.
- **Convenience accessors** — flat summary shortcuts
  (`pistol_team1` / `converted_team1` / `bonus_team1` and the
  `_team2` counterparts), `full_buy` / `half_buy` / `eco` aliases on
  `TeamBuyMatrix`, and a combined `total` on `BuyTierRecord` for the
  overall won/total on a tier regardless of the opponent's buy type.
- **Round economy in `series.rounds`** — `RoundData` now carries the
  per-round economy from the economy tab: `bank_team1`/`bank_team2`,
  `spent_team1`/`spent_team2`, `buy_type_team1`/`buy_type_team2`, and
  `is_pistol_round`. `series.rounds` fetches and merges the economy tab
  automatically (economy fields stay `None`/empty when that page is
  unavailable), making it the single round-by-round source alongside
  `win_type` and the winner's `side`.
- **Series replay (logs tab)** — new `series.replay(series_id, game_id)`
  returning the per-round kill-feed timeline (`ReplayData` /
  `ReplayRound` / `ReplayEvent`): events typed by the `ReplayEventType`
  enum (`KILL`, `PLANT`, `DEFUSE`, plus derived `BOOM` detonation and
  `RESURRECT` events with `derived=True`, since vlr.gg logs neither as
  feed rows), round clocks in both display (`clock`) and numeric
  (`seconds`) form, kill cause (weapon or ability, e.g. `Sheriff`,
  `Overdrive`, `Tour de Force`, `Spike`), killer/victim positions with
  distance in minimap units, spike sites, and per-event alive snapshots
  (name, agent, team, side, minimap coordinates, facing angle). Each
  `ReplayRound` also includes `loadouts` (`list[PlayerRoundLoadout]`)
  and the `loadout_for(player)` helper, capturing every player's
  equipped weapon at round start, armor (supporting `No armor`,
  `Light armor`, `Heavy armor`, and `Regen Shield`), and credits
  left / spent in the buy phase. Real vlr.gg team and player IDs are
  resolved from the game's overview tab
  (one extra request, `team1_id`/`team2_id` and `player_id` fields) and
  matched strictly within each player's team so duplicate names never
  cross teams; unplayed maps or maps without round data return an
  empty timeline gracefully.
- **Series head-to-head history** — `SeriesInfo.head_to_head` exposes
  previous meetings between the two teams, parsed from the same overview
  page. Each `SeriesHeadToHeadMatch` includes the series ID/URL, event,
  stage, date, both team names/scores, and which side won.
- **Series streams in `series.vods()`** — `SeriesVods.streams` now contains
  live broadcasts and watch-party streams alongside the existing `vods`
  list. Each `SeriesStream` exposes the platform, channel, URL, stream
  type, and country code. `SeriesVod` also gains `platform`, `map_number`,
  and `start_seconds`.
- **Player total winnings** — `PlayerInfo.total_winnings` and
  `total_winnings_currency` now expose the total from the player's Event
  Placements card.
- **New `player.placements()` namespace** — returns `PlayerPlacements` with
  individual `PlayerEventPlacement` rows (event, year, stage, placement,
  prize, team) and the player's total winnings.
- **New grand-final fixtures** — series 130685 (LOUD vs OpTic, Champions
  2022 GF) and 754737 (LOUD vs Vitality, Champions 2026 GF) are now
  covered by tests across economy, info/pick-bans, players, rounds, and
  performance parsers.

### Fixed

- **`team.upcoming_matches()` no longer returns completed matches** — the
  parser now scopes its search to the heading's section wrapper instead of
  the whole team-summary column, so "Recent Results" is excluded.
- **`series.info()` on upcoming/live series** — `best_of` is now read from
  whichever match-header note contains the format (vlr.gg renders the
  countdown twice before `BoN`), and `TBD` map tabs are no longer marked
  `played`.
- **`team.completed_matches()` pagination** — added `limit` (default `50`)
  and `return_all`; extra pages are fetched only when the requested limit
  needs them. `TeamCompletedMatches.has_next_page` reports whether more
  matches exist beyond the returned results.
- **Team match `stage`/`bracket`** — both fields are now parsed separately
  from the team matches page (e.g. `stage="Playoffs"`, `bracket="LBF"`),
  and enrichment no longer concatenates them into `"Playoffs - LBF"`.
- **Parser whitespace** — shared `normalize_whitespace()` collapses raw tabs,
  newlines, and repeated spaces in parsed event/stage/bracket/role values
  instead of leaving values such as `"Playoffs ⋅\n\t\t\tLBF"`.
- **`events.matches()` team countries** — `MatchTeam` now exposes
  `country_name`, parsed from the team flag on the event matches page.
- **Thread-local HTTP client lifecycle** — parallel requests now reuse
  thread-local clients and close every client after fetching or enrichment,
  reducing client-creation overhead and preventing resource leaks.

### Changed

- **`RoundData.win_type` is now a `RoundWinType` enum** instead of a
  human-readable string. Use `round.win_type.full_name` for display text and
  `round.win_type.value` (`"elimination"`, `"defuse"`, `"spike_detonation"`,
  `"time_expired"`) for the raw value.

### Documentation

- Series economy reference updated for the new `BuyType` values,
  buy-matrix fields, and nested models; series rounds reference updated
  for the merged per-round economy fields; new series replay reference
  page for the kill-feed timeline module.
- Updated the `team.completed_matches`, `team.upcoming_matches`,
  `events.matches`, and `series.rounds` references for `bracket`,
  `country_name`, and the `RoundWinType` enum.
- Updated `series.info`, `series.vods`, and `player.info`, and added a
  `player.placements` reference for head-to-head history, streams, VOD
  metadata, and event placements.

## [2.4.1] - 2026-10-17

### Fixed

- **Series players/stats parsing** — newer vlr.gg overview tables add a
  dedicated `.mod-agents` cell before the stat columns. Stat cells are now
  mapped dynamically around that column, and agents are read from the new
  cell. This fixes `SideStats` validation errors and misaligned values
  (rating, ACS, KDA, KAST, ADR, HS%, first kills/deaths).
- **Series economy parsing** — the round-by-round economy grid now uses the
  newer `.vlr-rounds.ecr` markup (`.ecr-bank`, `.ecc-c`, `.ecc-sq`). Banks,
  spends, buy types, and round winners are read from it, with the legacy
  `.wf-table-inset.mod-econ` table kept as a fallback.
- **Series VODs parsing** — VODs are now read from the newer `.sm-vods`
  module (`.sm-vod-name` labels, `a.sm-ext` links), keeping the legacy
  `.match-vods` container as a fallback.
- **Series game map names** — the game header now renders the duration as a
  sibling of the map name. The map name is read from `.map-name`, so the
  duration is no longer concatenated (e.g. `Pearl` instead of `Pearl35:48`).

### Changed

- **Series economy team matching** — team/abbreviation resolution is now
  case-insensitive, so team IDs resolve for pages that render short tags.
- **HTML parsing backend** — parsing now uses selectolax's Lexbor engine
  (`selectolax.lexbor`) instead of the discontinued Modest engine
  (`selectolax.parser`), which selectolax removed in 1.0. This is an internal
  change: the public API, CSS selectors, and parsed output are unchanged.
- **Dependencies** — raised the `selectolax` minimum to `>=1.0.0` and moved
  `pydantic` to the 2.14 series.

### Documentation

- **Changelog** — this release is mirrored across `CHANGELOG.md`, the
  ReadTheDocs changelog, and the official site changelog.

## [2.4.0] - 2026-08-19

### Added

- **Bo1 series support** — single-map series now resolve games from
  `.vm-stats-game` containers when nav tabs are absent. `resolve_game_id`
  raises `ParsingError` instead of silently returning wrong data on
  out-of-range or empty game lists.
- **Event region resolution** — `_parse_breadcrumb` resolves `subregion=`
  breadcrumb links (e.g. "Japan", "North America") to their parent region
  via `commons.regions.resolve_subregion_to_region`. A new
  `EventRegion.subregion` field preserves the original subregion name
  (e.g. `"Japan"`); `None` for `region=` links.
- **Event country-to-region fallback** — when no breadcrumb region is
  present, the `region_location` country flag is resolved via
  `resolve_country_to_region` to infer the parent region.
- **Event region deduplication** — duplicate region entries (from both
  `region=` and `subregion=` breadcrumbs for the same parent region)
  are collapsed, preferring the entry that carries a subregion name.
- **`commons.regions` module** — new shared utilities for region
  resolution: `VALID_REGIONS`, `SUBREGION_TO_REGION` (17 VCL/GC
  subregions), `COUNTRY_TO_REGION` (~100+ countries),
  `resolve_subregion_to_region`, and `resolve_country_to_region`.
- **`commons.__init__` re-exports** — `resolve_subregion_to_region`,
  `resolve_country_to_region`, `VALID_REGIONS`, `SUBREGION_TO_REGION`,
  and `COUNTRY_TO_REGION` are now re-exported from `vlrdevapi.commons`.
- **Series forfeit detection** — new `ForfeitInfo` model on
  `SeriesInfo.forfeit` exposes `forfeited`, `team`, `team_id`, and
  `reason` fields. Parser detects `"forfeited by TEAM"` in the
  `match-header-vs-note` element and maps the team name to the
  corresponding `team1`/`team2` for ID resolution. Note-level
  forfeit text (e.g. "Blind Esports Forfeit Map 2") is also parsed.
- **Series match notes** — new `SeriesInfo.notes` list captures
  non-veto `match-header-note` text such as technical pause warnings
  and lobby remake notices.

### Changed

- **Series economy enrichment** — team matching now tries abbreviation
  names from `.ovw-player-tag` elements first (e.g. "SEN"), then falls
  back to full team names. This fixes mismatches where the economy tab
  shows a different abbreviation than the overview header.
- **Series rounds enrichment** — same abbreviation-first matching
  strategy as economy.
- **Series info veto parsing** — Bo1 veto fallback now handles the
  "bans + decider" pattern (e.g. `"Ban1 remains"`) in addition to
  pick/ban. The PICK badge is excluded from map names via
  `span.text(deep=False)`.
- **Series info notes parsing** — the parser now iterates all
  `match-header-note` elements instead of only the first. This
  correctly separates forfeit reasons, informational notes, and
  map veto text when multiple notes are present.

### Fixed

- **Economy bank/spend parsing** — `int()` calls on `.rnd-sq` `title`
  attributes and `.rnd-num` text are wrapped in `try/except ValueError`;
  malformed values default to `0` instead of crashing the parser.
- **Event region from location country** — events that only have a
  "Location" label with a flag (no separate "Region" label) now resolve
  the region from `location.country` via `resolve_country_to_region`.
  Previously the country-to-region fallback only checked `region_location`.
- **Phantom pagination in matches** — terminal pages no longer report
  `has_next_page = True` (from DaviAlcanfor PR #50).

### Documentation

- **Event info reference** — `EventRegion` fields table now documents
  the `subregion` field. Region example demonstrates subregion access.
  `regions` field description explains deduplication and International
  collapse.
- **Series info reference** — `ForfeitInfo` fields table documents the
  new `forfeit` nested model. `notes` field description explains the
  distinction between forfeit reasons and informational notes.
- **Series economy reference** — docstrings reference correct model
  types (`RoundEconomyData`, `bank_team1`).
- **Series rounds reference** — docstrings reference correct model
  types (`RoundData`, `winner_team_name`).
- **`commons.regions` module** — docstrings describe all mapping
  dictionaries and resolution functions.
- **Project structure** — contributing guide updated with actual
  underscore-prefixed directory names and new modules (`_news/`,
  `_utils/`, `commons/regions.py`).
- **Module docstrings** — added to `economy/parser.py`,
  `rounds/parser.py`, and `commons/__init__.py`.

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
