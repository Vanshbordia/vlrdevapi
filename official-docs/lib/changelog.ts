/**
 * Release notes for VLRdevAPI.
 *
 * Kept as typed data rather than MDX so the changelog timeline can render the
 * exact structured layout it needs. `date` is the human-readable form;
 * `isoDate` is the machine-readable form used by `<time dateTime>` and the
 * sitemap.
 */

export type ChangelogSection = {
  title: string
  items: string[]
}

export type ChangelogVersion = {
  version: string
  /** Human-readable release date, e.g. `23 October 2026`. */
  date: string
  /** Machine-readable release date, e.g. `2026-10-23`. */
  isoDate: string
  github: string
  pypi: string
  summary: string
  sections: ChangelogSection[]
}

export const versions = [
  {
    version: '3.0.0',
    date: '23 October 2026',
    isoDate: '2026-10-23',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/3.0.0',
    pypi: 'https://pypi.org/project/vlrdevapi/3.0.0/',
    summary: 'Major economy and data release: re-tiered buy types, buy-type matrices, per-round economy, a kill-feed replay timeline, series head-to-head history and streams, player placements, a RoundWinType enum, and fixes across team, series, event, and HTTP-client handling.',
    sections: [
      {
        title: 'Breaking',
        items: [
          '`BuyType` re-tiered to match vlr.gg — the economy tab no longer uses its old four spend tiers. `SEMI_ECO` and `SEMI_BUY` are removed and the remaining tiers follow VLR\'s current categories based on total team spend: `ECO` (under 10k), `HALF_BUY` (10k–18k), and `FULL_BUY` (18k+). A new `PISTOL` member marks pistol-round buys (previously reported as `ECO`). Code switching on `BuyType.SEMI_ECO` / `BuyType.SEMI_BUY` needs updating; string values are `"Pistol"`, `"Eco"`, `"Half-buy"`, `"Full-buy"`.',
        ],
      },
      {
        title: 'Added',
        items: [
          'Buy-type matrix — `EconomyData` now carries the economy tab\'s buy-type matrix as `buy_matrix_team1` / `buy_matrix_team2` (`TeamBuyMatrix`): the Pistol / Conv. / Bonus summary and the `On Eco` / `On Half buy` / `On Full buy` records (`BuyTierRecord.vs_eco` / `vs_half` / `vs_full`), each a `won`/`total` `EconScore`. Unplayed matchups are `None`. `series.economy(game_id="all")` also returns the all-maps aggregate matrix instead of an empty result.',
          'Convenience accessors — flat summary shortcuts (`pistol_team1` / `converted_team1` / `bonus_team1` and the `_team2` counterparts), `full_buy` / `half_buy` / `eco` aliases on `TeamBuyMatrix`, and a combined `total` on `BuyTierRecord` for the overall won/total on a tier regardless of the opponent\'s buy type.',
          'Round economy in `series.rounds` — `RoundData` now carries the per-round economy from the economy tab: `bank_team1`/`bank_team2`, `spent_team1`/`spent_team2`, `buy_type_team1`/`buy_type_team2`, and `is_pistol_round`. `series.rounds` fetches and merges the economy tab automatically (economy fields stay `None`/empty when that page is unavailable).',
          'Series replay (logs tab) — new `series.replay(series_id, game_id)` returning the per-round kill-feed timeline (`ReplayData` / `ReplayRound` / `ReplayEvent`): events typed by the `ReplayEventType` enum (`KILL`, `PLANT`, `DEFUSE`, plus derived `BOOM` detonation and `RESURRECT` events with `derived=True`), round clocks in both display (`clock`) and numeric (`seconds`) form, kill cause, killer/victim positions with distance, spike sites, and per-event alive snapshots. Real vlr.gg team and player IDs are resolved from the game\'s overview tab and matched strictly within each team.',
          'Series head-to-head history — `SeriesInfo.head_to_head` exposes previous meetings between the two teams, parsed from the same overview page. Each `SeriesHeadToHeadMatch` includes the series ID/URL, event, stage, date, both team names/scores, and which side won.',
          'Series streams in `series.vods()` — `SeriesVods.streams` now contains live broadcasts and watch-party streams alongside the existing `vods` list. Each `SeriesStream` exposes the platform, channel, URL, stream type, and country code. `SeriesVod` also gains `platform`, `map_number`, and `start_seconds`.',
          'Player total winnings — `PlayerInfo.total_winnings` and `total_winnings_currency` now expose the total from the player\'s Event Placements card.',
          'New `player.placements()` namespace — returns `PlayerPlacements` with individual `PlayerEventPlacement` rows (event, year, stage, placement, prize, team) and the player\'s total winnings.',
          'New grand-final fixtures — series 130685 (LOUD vs OpTic, Champions 2022 GF) and 754737 (LOUD vs Vitality, Champions 2026 GF) are now covered by tests across economy, info/pick-bans, players, rounds, and performance parsers.',
        ],
      },
      {
        title: 'Fixed',
        items: [
          '`team.upcoming_matches()` no longer returns completed matches — the parser now scopes its search to the heading\'s section wrapper instead of the whole team-summary column, so "Recent Results" is excluded.',
          '`series.info()` on upcoming/live series — `best_of` is now read from whichever match-header note contains the format (vlr.gg renders the countdown twice before `BoN`), and `TBD` map tabs are no longer marked `played`.',
          '`team.completed_matches()` pagination — added `limit` (default `50`) and `return_all`; extra pages are fetched only when the requested limit needs them. `TeamCompletedMatches.has_next_page` reports whether more matches exist beyond the returned results.',
          'Team match `stage`/`bracket` — both fields are now parsed separately from the team matches page (e.g. `stage="Playoffs"`, `bracket="LBF"`), and enrichment no longer concatenates them into `"Playoffs - LBF"`.',
          'Parser whitespace — shared `normalize_whitespace()` collapses raw tabs, newlines, and repeated spaces in parsed event/stage/bracket/role values instead of leaving values such as `"Playoffs ⋅\\n\\t\\t\\tLBF"`.',
          '`events.matches()` team countries — `MatchTeam` now exposes `country_name`, parsed from the team flag on the event matches page.',
          'Thread-local HTTP client lifecycle — parallel requests now reuse thread-local clients and close every client after fetching or enrichment, reducing client-creation overhead and preventing resource leaks.',
        ],
      },
      {
        title: 'Changed',
        items: [
          '`RoundData.win_type` is now a `RoundWinType` enum instead of a human-readable string. Use `round.win_type.full_name` for display text and `round.win_type.value` (`"elimination"`, `"defuse"`, `"spike_detonation"`, `"time_expired"`) for the raw value.',
        ],
      },
      {
        title: 'Documentation',
        items: [
          'Series economy reference updated for the new `BuyType` values, buy-matrix fields, and nested models; series rounds reference updated for the merged per-round economy fields; new series replay reference page for the kill-feed timeline module.',
          '`team.completed_matches`, `team.upcoming_matches`, `events.matches`, and `series.rounds` references updated for `bracket`, `country_name`, and the `RoundWinType` enum.',
          '`series.info`, `series.vods`, and `player.info` updated, and a `player.placements` reference added for head-to-head history, streams, VOD metadata, and event placements.',
        ],
      },
    ],
  },
  {
    version: '2.4.1',
    date: '17 October 2026',
    isoDate: '2026-10-17',
    github: 'https://github.com/vanshbordia/vlrdevapi/releases/tag/2.4.1',
    pypi: 'https://pypi.org/project/vlrdevapi/2.4.1/',
    summary: 'Fixes series player-stat, economy, VOD, and map-name parsing for the latest vlr.gg markup, makes economy team matching case-insensitive, and moves HTML parsing to selectolax\'s Lexbor engine.',
    sections: [
      {
        title: 'Fixed',
        items: [
          'Series players/stats parsing — newer vlr.gg overview tables add a dedicated `.mod-agents` cell before the stat columns. Stat cells are now mapped dynamically around that column, and agents are read from the new cell. This fixes `SideStats` validation errors and misaligned values (rating, ACS, KDA, KAST, ADR, HS%, first kills/deaths).',
          'Series economy parsing — the round-by-round economy grid now uses the newer `.vlr-rounds.ecr` markup (`.ecr-bank`, `.ecc-c`, `.ecc-sq`). Banks, spends, buy types, and round winners are read from it, with the legacy `.wf-table-inset.mod-econ` table kept as a fallback.',
          'Series VODs parsing — VODs are now read from the newer `.sm-vods` module (`.sm-vod-name` labels, `a.sm-ext` links), keeping the legacy `.match-vods` container as a fallback.',
          'Series game map names — the game header now renders the duration as a sibling of the map name. The map name is read from `.map-name`, so the duration is no longer concatenated (e.g. `Pearl` instead of `Pearl35:48`).',
        ],
      },
      {
        title: 'Changed',
        items: [
          'Series economy team/abbreviation resolution is now case-insensitive, so team IDs resolve for pages that render short tags.',
          'HTML parsing backend — parsing now uses selectolax\'s Lexbor engine (`selectolax.lexbor`) instead of the discontinued Modest engine (`selectolax.parser`), which selectolax removed in 1.0. This is an internal change: the public API, CSS selectors, and parsed output are unchanged.',
          'Dependencies — raised the `selectolax` minimum to `>=1.0.0` and moved `pydantic` to the 2.14 series.',
        ],
      },
    ],
  },
  {
    version: '2.4.0',
    date: '19 August 2026',
    isoDate: '2026-08-19',
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
    isoDate: '2026-08-11',
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
    isoDate: '2026-08-11',
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
    isoDate: '2026-08-07',
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
    isoDate: '2026-07-29',
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
    isoDate: '2026-07-07',
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

/** Date of the most recent release, used as the changelog's `lastModified`. */
export const latestChangelogDate = new Date(`${versions[0].isoDate}T00:00:00Z`)
