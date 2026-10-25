<div align="center">

<img src="official-docs/public/logo.png" width="120" alt="vlrdevapi logo">

# vlrdevapi

**The modern, type-safe Python library for VLR.gg Valorant esports data**

[![PyPI version](https://img.shields.io/pypi/v/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![Python Version](https://img.shields.io/pypi/pyversions/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-vlrdevapi.pages.dev-blue.svg)](https://vlrdevapi.pages.dev/docs/)

[Documentation](https://vlrdevapi.pages.dev/docs/) · [Quickstart](https://vlrdevapi.pages.dev/docs/quickstart/) · [API Reference](https://vlrdevapi.pages.dev/docs/reference/) · [Guides](https://vlrdevapi.pages.dev/guides/) · [Changelog](https://vlrdevapi.pages.dev/changelog/) · [PyPI](https://pypi.org/project/vlrdevapi/)

</div>

---

**vlrdevapi** is a high-performance, type-safe Python client for extracting and analyzing Valorant esports data from [VLR.gg](https://www.vlr.gg/). Built for competitive analysts, data scientists, Discord bot creators, and esports engineers, it delivers structured [Pydantic](https://docs.pydantic.dev/) models with full type hinting, built-in rate limiting, automatic retries, and comprehensive coverage across all VLR.gg entities.

Whether you need live match tickers, tournament brackets, historical player ratings, round-by-round economy buy matrices, or 2D minimap kill-feed replay timelines with player loadouts, **vlrdevapi** provides a clean, idiomatic interface.

---

## Highlights

- **Universal Tabular Data Exports** — Seamlessly export any response into `pandas.DataFrame` (`.to_df()`), native `polars.DataFrame` (`.to_polars()`), `CSV` (`.to_csv()`), `Apache Parquet` (`.to_parquet()`), `Excel` (`.to_excel()`), formatted `JSON` (`.to_json()`), and `Markdown` (`.to_markdown()`).
- **Model Context Protocol (MCP) Server** — Connect Claude Desktop, Cursor, Zed, and AI agents directly to live Valorant data via the built-in `vlrdevapi-mcp` stdio server with 41 tools.
- **Complete Valorant Esports Coverage** — Tournaments, match schedules, live scoreboards, player careers, team rosters, roster transactions, and esports news.
- **2D Kill-Feed Replay Timelines** — Spatial `(x, y)` kill coordinates, viewing angles, kill distances, plant/defuse events, spike detonations (`boom`), resurrections, alive player snapshots, and buy-phase **player loadouts** (weapons, shields, spent credits, remaining bank).
- **Round-by-Round Economy** — Full team buy matrices (`loadout_value`, `spent`, `bank`, buy classifications like `Eco`, `Anti-eco`, `Semi-buy`, `Semi-rifle`, and `Full buy`).
- **Strictly Typed Pydantic Models** — Every endpoint returns validated models with full field annotations, descriptive docstrings, and IDE autocompletion.
- **Production-Ready Reliability** — Built-in token-bucket rate limiter, exponential backoff retries, thread-safe connection pooling, and LRU-cached enrichment.
- **Flexible Access Patterns** — Use lightweight module-level calls (`vlrdevapi.player.info(...)`), curried ID chaining (`vlrdevapi.player(11225).info()`), or a managed context manager (`with VLRClient() as client:`).
- **Timezone Awareness** — Seamlessly convert match schedules and timestamps into any target timezone via Python's standard `zoneinfo`.
- **Managed with [uv](https://docs.astral.sh/uv/)** — Blazing fast dependency resolution and testing workflows.

---

## Installation

Install `vlrdevapi` using [uv](https://docs.astral.sh/uv/) (recommended) or `pip`:

```bash
# Basic installation
pip install vlrdevapi
# or with uv
uv add vlrdevapi

# With optional extras
pip install "vlrdevapi[pandas]"     # pandas.DataFrame (.to_df())
pip install "vlrdevapi[polars]"     # polars.DataFrame (.to_polars())
pip install "vlrdevapi[excel]"      # Excel .xlsx (.to_excel())
pip install "vlrdevapi[parquet]"    # Apache Parquet (.to_parquet())
pip install "vlrdevapi[mcp]"        # MCP server (vlrdevapi-mcp)

# Install with all optional extras
pip install "vlrdevapi[all]"
```

> **Requirements:** Python 3.11 or higher.

---

## Quickstart

### 1. Direct Module-Level Access (Zero Setup)

Fetch data immediately without instantiating a client:

```python
import vlrdevapi

# Get player profile and country
player = vlrdevapi.player.info(player_id=11225)
print(f"Player: {player.name} ({player.country})")

# Get series overview
series = vlrdevapi.series.info(series_id=542272)
print(f"Match: {series.team1.name} vs {series.team2.name} - Score: {series.score1}:{series.score2}")

# Get event details
event = vlrdevapi.event.info(event_id=2863)
print(f"Event: {event.name} ({event.start_date} to {event.end_date})")
```

### 2. Curried Method Chaining

Bind an ID once, then query multiple sub-methods without repeating the identifier:

```python
import vlrdevapi

# Bind team 2593 (FNATIC) once
fnc = vlrdevapi.team(2593)

info = fnc.info()
print(f"{info.name} [{info.tag}] - Country: {info.country}")

roster = fnc.roster()
print(f"Active Players: {[p.ign for p in roster.players]}")

placements = fnc.placements()
print(f"Total Prize Earnings: {placements.total_winnings_currency}{placements.total_winnings:,}")
```

### 3. Managed Client Session (`VLRClient`)

For production applications, high-throughput scripts, or custom concurrency tuning, use `VLRClient`:

```python
from vlrdevapi import VLRClient

with VLRClient(timeout=30, requests_per_second=8, max_retries=3) as client:
    # Live matches ticker
    live_matches = client.matches.live()
    for m in live_matches.matches:
        print(f"LIVE: {m.team1.name} vs {m.team2.name} ({m.event})")

    # Series performance & economy
    series = client.series(542272)
    econ = series.economy(game_id=1)
    print(f"Map 1 Rounds Analyzed: {len(econ.rounds)}")
```

---

## API Overview & Reference

| Module | Key Methods | Description | Official Docs |
|:---|:---|:---|:---|
| **[Matches](https://vlrdevapi.pages.dev/docs/reference/matches/)** | `upcoming()`, `live()`, `completed()` | Live scores, upcoming schedules, and paginated match history | [Docs →](https://vlrdevapi.pages.dev/docs/reference/matches/) |
| **[Series](https://vlrdevapi.pages.dev/docs/reference/series/)** | `info()`, `replay()`, `economy()`, `players()`, `rounds()`, `vods()`, `performance()` | Deep map analytics, kill-feed timeline, buy matrices, player stats, and streams | [Docs →](https://vlrdevapi.pages.dev/docs/reference/series/) |
| **[Players](https://vlrdevapi.pages.dev/docs/reference/player/)** | `info()`, `profile()`, `agents()`, `teams()`, `matches()`, `placements()` | Historical ratings (ACS, K/D, ADR, KAST), agent pools, career history, and placements | [Docs →](https://vlrdevapi.pages.dev/docs/reference/player/) |
| **[Teams](https://vlrdevapi.pages.dev/docs/reference/team/)** | `info()`, `roster()`, `placements()`, `transactions()`, `completed_matches()`, `upcoming_matches()` | Active rosters, staff, roster transfers, historical match records, and tournament earnings | [Docs →](https://vlrdevapi.pages.dev/docs/reference/team/) |
| **[Events](https://vlrdevapi.pages.dev/docs/reference/events/)** | `info()`, `stages()`, `matches()`, `standings()`, `teams()`, `list()` | Tournament brackets, group/playoff stages, standings, prize pools, and participating teams | [Docs →](https://vlrdevapi.pages.dev/docs/reference/events/) |
| **[News](https://vlrdevapi.pages.dev/docs/reference/news/)** | `list()`, `article()` | VLR.gg editorial articles, breaking roster news, author details, and full Markdown content | [Docs →](https://vlrdevapi.pages.dev/docs/reference/news/) |

---

## Code Examples

### 1. Spatial Replay Timeline & Round Loadouts

Inspect round-by-round kill events with 2D minimap locations, viewing angles, distances, and player equipment:

```python
import vlrdevapi

# Fetch replay timeline for Game 3 of a series (Sunset)
replay = vlrdevapi.series.replay(series_id=754737, game_id=283288)
round_1 = replay.round(1)

if round_1:
    print(f"Round 1 Attacking Side: {round_1.attacking}")

    # Check buy-phase loadout for a player
    loadout = round_1.loadout_for("Derke")
    if loadout:
        print(f"Derke: Weapon={loadout.weapon}, Armor={loadout.armor}, Spent=${loadout.spent}")

    # Iterate through kill events
    for event in round_1.events:
        if event.type.value == "kill":
            killer = event.actor.name if event.actor else "World"
            victim = event.victim.name if event.victim else "Unknown"
            dist = f"{event.distance_units:.1f}u" if event.distance_units else "N/A"
            print(f"  [{event.clock}] {killer} killed {victim} with {event.cause} (dist: {dist})")
            if event.pos_x is not None:
                print(f"    Victim pos: ({event.pos_x}, {event.pos_y}) | Killer pos: ({event.from_x}, {event.from_y})")
```

Learn more in the [Series Replay Documentation](https://vlrdevapi.pages.dev/docs/reference/series/replay/).

---

### 2. Round Economy & Team Buy Matrices

Analyze team spending, bank reserves, and buy types across rounds:

```python
import vlrdevapi

economy = vlrdevapi.series.economy(series_id=754737, game_id=283288)

for r in economy.rounds[:5]:
    winner_name = r.winner.name if r.winner else "Unknown"
    print(f"Round {r.round_number}: Winner = {winner_name}")
    print(f"  {economy.team1}: {r.buy_type_team1} (Spent: ${r.spent_team1:,}, Bank: ${r.bank_team1:,})")
    print(f"  {economy.team2}: {r.buy_type_team2} (Spent: ${r.spent_team2:,}, Bank: ${r.bank_team2:,})")
```

Learn more in the [Series Economy Documentation](https://vlrdevapi.pages.dev/docs/reference/series/economy/).

---

### 3. Player Career Statistics & Agent Pools

Extract ACS, K/D, KAST, and ADR broken down by agent:

```python
import vlrdevapi

# Query player agent stats over the last 60 days
agent_stats = vlrdevapi.player.agents(player_id=11225, timespan="60d")

for a in agent_stats.agents[:4]:
    print(f"{a.agent:<10} | Pick Rate: {a.use} | Rating: {a.rating} | ACS: {a.acs} | K/D: {a.kd}")
```

Learn more in the [Player Reference Documentation](https://vlrdevapi.pages.dev/docs/reference/player/).

---

### 4. Tournament Brackets & Standings

Fetch event stages, match schedules, and final prize distributions:

```python
import vlrdevapi

event_id = 2863  # e.g., Champions 2026
event = vlrdevapi.event(event_id)

# Event stages (Group Stage, Playoffs, etc.)
for stage in event.stages():
    print(f"Stage: {stage.name} (ID: {stage.id})")

# Final event standings & prize earnings
standings = event.standings()
for stage in standings.stages[:1]:
    print(f"--- {stage.stage_name} ---")
    for row in stage.standings[:3]:
        team_name = row.team.name if row.team else "TBD"
        prize = f"{row.prize_currency}{row.prize_money:,}" if row.prize_money else "N/A"
        print(f"  #{row.place}: {team_name} - Prize: {prize}")
```

Learn more in the [Events Reference Documentation](https://vlrdevapi.pages.dev/docs/reference/events/).

---

### 5. News Articles with Full Markdown

Read VLR.gg editorial content formatted in clean GitHub-flavored Markdown:

```python
import vlrdevapi

# Get latest articles
feed = vlrdevapi.news(page=1)
latest = feed.news[0]

# Retrieve full article body
article = vlrdevapi.news.article(latest.id)
print(f"Title:  {article.title}")
print(f"Author: {article.author} ({article.date})")
print(f"Length: {len(article.content_md):,} characters")
```

Learn more in the [News Reference Documentation](https://vlrdevapi.pages.dev/docs/reference/news/).

---

## Tabular Data Exports (Data Science & Analytics)

Every response model inherits from `ExportableModel`, enabling instant conversion to dataframes, spreadsheets, and serialized files:

```python
import vlrdevapi

# 1. Fetch player statistics for a grand final
players = vlrdevapi.series(754737).players()

# 2. Convert to pandas DataFrame
df = players.to_df()
print(df[["player_name", "team_name", "rating", "acs", "kd"]].head())

# 3. Convert to Polars DataFrame (preserving typed list columns)
polars_df = players.to_polars()

# 4. Export to CSV (semicolon-delimited lists, e.g. "neon;raze;jett")
players.to_csv("grand_final_players.csv")

# 5. Export to Apache Parquet
players.to_parquet("grand_final_players.parquet")

# 6. Export to Excel (.xlsx)
players.to_excel("grand_final_players.xlsx", sheet_name="PlayerStats")

# 7. Export to JSON (in-memory string or written to disk)
json_payload = players.to_json(indent=2)

# 8. Print GitHub-flavored Markdown table
print(players.to_markdown())
```

---

## Model Context Protocol (MCP) Server

VLRdevAPI includes a native MCP server for AI assistants and autonomous coding agents:

```bash
# Run server over stdio
vlrdevapi-mcp

# Or zero-install with uvx
uvx --from "vlrdevapi[mcp]" vlrdevapi-mcp
```

### Claude Desktop & Cursor Integration

Add to your `claude_desktop_config.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "vlrdevapi": {
      "command": "uvx",
      "args": ["--from", "vlrdevapi[mcp]", "vlrdevapi-mcp"]
    }
  }
}
```

The MCP server provides **41 tools** covering matches, series, teams, players, tournaments, and editorial news, plus high-level composite tools (`get_match_full_context`, `get_team_overview`, `compare_teams`, `get_player_career_summary`, `get_h2h_matchup`, `get_tournament_dossier`, `get_live_and_upcoming_schedule`, `get_news_digest`, `series_map_summary`).

---

## Configuration & Error Handling

### Rate Limiting & Concurrency

`vlrdevapi` includes sensible defaults (`4.0` requests per second) to respect VLR.gg servers. When using `VLRClient`, you can customize client settings:

```python
from zoneinfo import ZoneInfo
from vlrdevapi import VLRClient

client = VLRClient(
    timeout=20,                     # Timeout per request (seconds)
    requests_per_second=6,          # Max rate limit
    max_retries=4,                  # Exponential backoff retries
    source_tz=ZoneInfo("America/New_York"),  # Target timezone for schedules
)
```

### Typed Exceptions

Catch errors with specific, typed exception classes from `vlrdevapi.exceptions`:

```python
import vlrdevapi
from vlrdevapi.exceptions import (
    NotFoundError,
    RateLimitError,
    RequestError,
    ValidationError,
)

try:
    player = vlrdevapi.player.info(player_id=99999999)
except NotFoundError:
    print("Player not found on VLR.gg (404).")
except RateLimitError:
    print("Exceeded VLR.gg rate limits. Please slow down requests.")
except ValidationError as e:
    print(f"Invalid parameter passed: {e}")
except RequestError as e:
    print(f"Network error occurred: {e}")
```

---

## Documentation & Guides

Comprehensive documentation, tutorials, and deep-dives are available on the official documentation portal:

- **[Documentation Home](https://vlrdevapi.pages.dev/docs/)** — Complete getting-started guide and architectural overview.
- **[Quickstart Guide](https://vlrdevapi.pages.dev/docs/quickstart/)** — First queries in under two minutes.
- **[Series Replay Guide](https://vlrdevapi.pages.dev/docs/reference/series/replay/)** — Mapping 2D replay coordinates, viewing angles, and equipment.
- **[Series Economy Guide](https://vlrdevapi.pages.dev/docs/reference/series/economy/)** — Round spending and buy matrix mechanics.
- **[Guides & Tutorials](https://vlrdevapi.pages.dev/guides/)** — Real-world guides for Discord bots, Pandas analysis, and Polars pipelines.
- **[Frequently Asked Questions](https://vlrdevapi.pages.dev/faq/)** — Common questions on rate limits, IDs, and data structures.
- **[Changelog](https://vlrdevapi.pages.dev/changelog/)** — Version history and release notes.

---

## Development

Contributions and bug reports are welcome! This repository uses `uv` for package management and testing:

```bash
# 1. Clone the repository
git clone https://github.com/Vanshbordia/vlrdevapi.git
cd vlrdevapi

# 2. Install dependencies with uv
uv sync --group dev

# 3. Run the unit test suite
uv run pytest tests/ -v

# 4. Run static type checking and linter
uv run ruff check src/ tests/
```

Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting pull requests.

---

## License

This project is licensed under the [MIT License](LICENCE).

---

## Disclaimer

`vlrdevapi` is an independent open-source library. It is not affiliated with, maintained, authorized, or endorsed by [VLR.gg](https://www.vlr.gg/) or [Riot Games](https://www.riotgames.com/). Valorant and all associated properties are trademarks or registered trademarks of Riot Games, Inc. Please use responsibly and respect VLR.gg's bandwidth and server infrastructure.
