<div align="center">

<img src="official-docs/public/logo.svg" width="120" alt="vlrdevapi logo">

# vlrdevapi

**Python library for VLR.gg Valorant esports data**

[![Python Version](https://img.shields.io/pypi/pyversions/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![PyPI](https://img.shields.io/pypi/v/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Documentation](https://vlrdevapi.pages.dev/docs) · [ReadTheDocs](https://vlrdevapi.readthedocs.io/) · [PyPI](https://pypi.org/project/vlrdevapi/) · [GitHub](https://github.com/Vanshbordia/vlrdevapi)

</div>

---

Access Valorant esports data from VLR.gg with a clean, type-safe Python API. Get tournament info, match schedules, player stats, team data, and series/match-level details.

## Features

- **Complete Data Access** - Events, matches, players, teams, and series
- **Type-Safe** - Pydantic models with rich type hints and field descriptions
- **Production-Ready** - Retry logic, rate limiting, and LRU-cached enrichment
- **Curried Access** - Bind a player/team/series ID once, then call sub-methods without re-passing
- **Managed with [uv](https://docs.astral.sh/uv/)** - Fast dependency resolution and virtual environment management

## Installation

```bash
# Using uv (recommended)
uv add vlrdevapi

# Using pip
pip install vlrdevapi
```

Requires Python 3.11+

## Quick Start

### Module-level (no client needed)

```python
import vlrdevapi

# Single-shot fetches via module-level access
info = vlrdevapi.player.info(player_id=11225)
print(f"{info.name} - {info.country}")

series = vlrdevapi.series.info(series_id=542272)
print(f"{series.team1.name} vs {series.team2.name}")

event = vlrdevapi.event.info(event_id=2863)
print(f"{event.name} - {event.subtitle}")
```

### Sync client

```python
from vlrdevapi import VLRClient

with VLRClient() as client:
    # Curried access - bind a player once
    player = client.player(11225)
    print(player.info().name)
    print(player.teams().current_teams)
    print(player.agents(timespan="all").agents[:3])

    # Team data
    team = client.team(1034)
    roster = team.roster()
    placements = team.placements()

    # Event data
    event = client.event(2863)
    stages = event.stages()
    matches = event.matches()
```

## API Modules

### Matches

```python
matches = client.matches.upcoming(page=1)
live = client.matches.live()
completed = client.matches.completed(page=1)
```

### Players

```python
p = client.player(11225)
info = p.info()                           # Basic info
teams = p.teams()                         # Current / past teams
agents = p.agents(timespan="60d")         # Agent stats
matches = p.matches(limit=20)             # Match history
profile = p.profile()                     # Consolidated profile
```

### Teams

```python
t = client.team(1034)
info = t.info()                           # Name, tag, socials
roster = t.roster()                       # Players + staff
placements = t.placements()               # Event placements + winnings
transactions = t.transactions()            # Join / leave history
completed = t.completed_matches()          # Completed match results
upcoming = t.upcoming_matches()            # Upcoming match schedule
```

### Events

```python
e = client.event(2863)
info = e.info()                          # Event details
matches = e.matches()                    # Match list
standings = e.standings()                # Standings / prize distribution
```

### Series

```python
s = client.series(542272)
info = s.info()                          # Series overview
vods = s.vods()                          # VOD links
players = s.players(game_id=1)           # Per-game player stats
rounds = s.rounds(game_id=1)             # Round-by-round data
performance = s.performance()            # Advanced performance stats
economy = s.economy(game_id=1)           # Economy data
```

## Documentation

- **Official Docs** - [vlrdevapi.pages.dev/docs](https://vlrdevapi.pages.dev/docs)
- **ReadTheDocs** - [vlrdevapi.readthedocs.io](https://vlrdevapi.readthedocs.io/)

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone and set up
git clone https://github.com/Vanshbordia/vlrdevapi
cd vlrdevapi
uv sync --group dev

# Lint & type check
ruff check src/ tests/
ty check src/vlrdevapi/

# Run tests
uv run pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

## License

MIT License - see the [LICENCE](LICENCE) file.

---

**Disclaimer:** Not affiliated with VLR.gg or Riot Games. Use responsibly.
