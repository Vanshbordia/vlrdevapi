# vlrdevapi

[![PyPI version](https://badge.fury.io/py/vlrdevapi.svg)](https://badge.fury.io/py/vlrdevapi)
[![Python Version](https://img.shields.io/pypi/pyversions/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/vlrdevapi/badge/?version=latest)](https://vlrdevapi.readthedocs.io/en/latest/?badge=latest)

**Python library for VLR.gg Valorant esports data**

Access Valorant esports data from VLR.gg with a clean, type-safe Python API. Get tournament info, match schedules, player stats, team data, and more.

## Features

- **Complete Data Access**: Events, matches, players, teams, series, and search
- **Type-Safe**: Frozen Python dataclasses with rich type hints
- **Production-Ready**: Error handling, retry logic, and rate limiting
- **Easy to Use**: Simple, intuitive API design

## Installation

```bash
pip install vlrdevapi
```

Requires Python 3.11+

## Quick Start

```python
import vlrdevapi as vlr

# Search for anything
results = vlr.search.search("nrg")
print(f"Found {results.total_results} results")

# Get upcoming matches
matches = vlr.matches.upcoming(limit=5)
for match in matches:
    print(f"{match.team1.name} vs {match.team2.name}")

# Player stats
profile = vlr.players.profile(player_id=4164)
print(f"{profile.handle} - {profile.country}")

# Team info
team = vlr.teams.info(team_id=1034)
print(f"{team.name} ({team.tag})")

# Event details
events = vlr.events.list_events(tier="vct", status="ongoing")
```

## API Modules

### Search
```python
# Search everything
results = vlr.search.search("nrg")

# Type-specific searches
players = vlr.search.search_players("tenz")
teams = vlr.search.search_teams("sentinels")
events = vlr.search.search_events("champions")
```

### Matches
```python
# Get matches
upcoming = vlr.matches.upcoming(limit=10)
live = vlr.matches.live()
completed = vlr.matches.completed(limit=10)
```

### Players
```python
# Player data
profile = vlr.players.profile(player_id=4164)
matches = vlr.players.matches(player_id=4164, limit=20)
stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
```

### Teams
```python
# Team data
info = vlr.teams.info(team_id=1034)
roster = vlr.teams.roster(team_id=1034)
matches = vlr.teams.upcoming_matches(team_id=1034)
placements = vlr.teams.placements(team_id=1034)
```

### Events
```python
# Event data
events = vlr.events.list_events(tier="vct", status="ongoing")
info = vlr.events.info(event_id=2498)
matches = vlr.events.matches(event_id=2498)
standings = vlr.events.standings(event_id=2498)
```

### Series
```python
# Match details
info = vlr.series.info(match_id=530935)
maps = vlr.series.matches(series_id=530935)
```

## Documentation

Full documentation available at [vlrdevapi.readthedocs.io](https://vlrdevapi.readthedocs.io/)

- [API Reference](https://vlrdevapi.readthedocs.io/en/latest/api/) - Complete function documentation
- [Examples](https://vlrdevapi.readthedocs.io/en/latest/examples.html) - Practical code examples
- [Installation Guide](https://vlrdevapi.readthedocs.io/en/latest/installation.html) - Setup instructions

## Common Use Cases

- Analytics dashboards and statistics trackers
- Tournament tracking and match notifications
- Player performance analysis
- Discord bots and automated reports
- Betting prediction models
- Research and data analysis

## FAQ

**Is this official?** No, VLR.gg has no official API. This is a community library.

**How do I find IDs?** Check VLR.gg URLs. Example: `vlr.gg/player/4164/aspas` → player ID is `4164`

**Python version?** Requires Python 3.11+

## Links

- [Documentation](https://vlrdevapi.readthedocs.io/)
- [GitHub](https://github.com/vanshbordia/vlrdevapi)
- [Issues](https://github.com/vanshbordia/vlrdevapi/issues)

## License

MIT License - see LICENSE file

---

**Disclaimer:** Not affiliated with VLR.gg or Riot Games. Use responsibly.
