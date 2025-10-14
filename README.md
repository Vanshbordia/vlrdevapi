# vlrdevapi

[![PyPI version](https://badge.fury.io/py/vlrdevapi.svg)](https://badge.fury.io/py/vlrdevapi)
[![Python Version](https://img.shields.io/pypi/pyversions/vlrdevapi.svg)](https://pypi.org/project/vlrdevapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/vlrdevapi/badge/?version=latest)](https://vlrdevapi.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/vanshbordia/vlrdevapi/workflows/tests/badge.svg)](https://github.com/vanshbordia/vlrdevapi/actions)

**The Python library for VLR.gg Valorant esports data scraping and API access.**

vlrdevapi is a comprehensive, type-safe Python client library designed specifically for scraping and accessing Valorant esports data from VLR.gg. As there is no official VLR.gg API, this library provides a standardized, reliable, and efficient way to programmatically access tournament information, match data, player statistics, and more.

## Why vlrdevapi?

vlrdevapi is the fastest and most complete solution for Valorant esports data extraction:

- **Comprehensive Coverage**: Events, matches, players, series, teams, and statistics
- **Type-Safe**: Full Pydantic models with automatic validation
- **Production-Ready**: Built-in retry logic, error handling, and rate limit protection
- **Developer-Friendly**: Intuitive API design with extensive documentation
- **Well-Maintained**: Active development with regular updates
- **Open Source**: MIT licensed, community-driven development

## Key Features

### Data Access

| Feature | Description |
|---------|-------------|
| **Events API** | List, filter, and access tournament/event data including schedules, prize pools, and standings |
| **Matches API** | Get upcoming, live, and completed match information with real-time scores |
| **Players API** | Access player profiles, statistics, match history, and agent performance data |
| **Series API** | Detailed match analytics including map picks/bans, player stats, and round results |

### Technical Features

- **Type Safety**: Complete Pydantic model coverage with automatic validation
- **Error Handling**: Built-in retry logic with exponential backoff
- **Rate Limiting**: Automatic rate limit detection and handling
- **Caching**: Intelligent response caching to reduce API calls
- **Fast Parsing**: lxml-based HTML parsing for optimal performance
- **Connection Pooling**: Persistent HTTP connections for reduced latency

## Installation

Requires Python 3.11 or higher.

```bash
pip install vlrdevapi
```

### Development Installation

```bash
git clone https://github.com/vanshbordia/vlrdevapi.git
cd vlrdevapi
pip install -e .[dev]
```

## Quick Start

```python
import vlrdevapi as vlr

# List VCT events
events = vlr.events.list_events(tier="vct", status="ongoing")
for event in events:
    print(f"{event.name} - {event.status}")

# Get upcoming matches
matches = vlr.matches.upcoming(limit=5)
for match in matches:
    print(f"{match.teams[0]} vs {match.teams[1]} - {match.event}")

# Player profile and stats
profile = vlr.players.profile(player_id=4164)
print(f"{profile.handle} ({profile.real_name}) - {profile.country}")

agent_stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
for stat in agent_stats:
    print(f"{stat.agent}: {stat.rating} rating, {stat.acs} ACS")

# Series information
info = vlr.series.info(match_id=530935)
print(f"{info.teams[0].name} vs {info.teams[1].name}")
print(f"Score: {info.score[0]}-{info.score[1]}")
```

## Complete API Reference

### Teams Module - Team Information and Statistics

```python
import vlrdevapi as vlr

# Team information
team_info = vlr.teams.info(team_id=799)
print(f"{team_info.name} ({team_info.tag}) - {team_info.country}")

# Team roster
roster = vlr.teams.roster(team_id=799)
for member in roster:
    print(f"{member.ign} - {member.name}")

# Upcoming matches with pagination
upcoming = vlr.teams.upcoming_matches(team_id=799, count=10)

# Completed matches with pagination
completed = vlr.teams.completed_matches(team_id=799, count=20)

# Event placements
placements = vlr.teams.placements(team_id=799)
for placement in placements:
    print(f"{placement.event_name} ({placement.year})")
    for detail in placement.placements:
        print(f"  {detail.series} - {detail.place}: {detail.prize_money}")
```

### Events Module - Tournament and Competition Data

```python
import vlrdevapi as vlr

# List events with filters
events = vlr.events.list_events(
    tier="vct",           # "all", "vct", "vcl", "t3", "gc", "cg", "offseason"
    region="na",          # Optional region filter
    status="ongoing",     # "all", "upcoming", "ongoing", "completed"
    page=1
)

# Get event details
info = vlr.events.info(event_id=2498)

# Get event matches
matches = vlr.events.matches(event_id=2498)

# Get event standings
standings = vlr.events.standings(event_id=2498)
```

### Matches Module - Match Schedules and Results

```python
import vlrdevapi as vlr

# Upcoming matches
upcoming = vlr.matches.upcoming(limit=10)

# Live matches
live = vlr.matches.live()

# Completed matches
completed = vlr.matches.completed(limit=10, page=1)
```

### Players Module - Player Information and Statistics

```python
import vlrdevapi as vlr

# Player profile
profile = vlr.players.profile(player_id=4164)

# Player match history
matches = vlr.players.matches(player_id=4164, limit=20)

# Agent statistics
stats = vlr.players.agent_stats(
    player_id=4164,
    timespan="60d"  # "30d", "60d", "90d", "all"
)
```

### Series Module - Detailed Match Analytics

```python
import vlrdevapi as vlr

# Series/match information
info = vlr.series.info(match_id=530935)

# Detailed map statistics
maps = vlr.series.matches(series_id=530935)
for map_data in maps:
    print(f"Map: {map_data.map_name}")
    for player in map_data.players:
        print(f"  {player.name}: {player.k}/{player.d}/{player.a}")
```

## Data Models and Type Safety

All API responses are returned as immutable Pydantic models with complete type hints:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ListEvent` | Event list entries | id, name, status, dates, prize |
| `Info` | Detailed event data | name, prize, location, regions |
| `Match` | Match information | teams, score, event, status |
| `Profile` | Player profiles | handle, real_name, country, teams |
| `AgentStats` | Agent performance | agent, rating, acs, kd, kast |
| `MapPlayers` | Map statistics | map_name, players, teams, rounds |

### Model Features

- **Immutable**: All models are frozen after creation
- **Validated**: Automatic data validation using Pydantic
- **Serializable**: Easy conversion to dict/JSON
- **Type-Hinted**: Full IDE autocomplete support

```python
# Access model fields
profile = vlr.players.profile(player_id=4164)
print(profile.handle)  # IDE autocomplete works

# Convert to dictionary
data = profile.model_dump()

# Serialize to JSON
json_str = profile.model_dump_json()
```

## Use Cases

vlrdevapi is perfect for:

- **Data Analysis**: Build analytics dashboards and statistics trackers
- **Betting Tools**: Create prediction models and odds calculators  
- **Tournament Tracking**: Monitor ongoing events and match results
- **Player Scouting**: Analyze player performance across agents and maps
- **Content Creation**: Generate automated match reports and summaries
- **Discord Bots**: Real-time match notifications and statistics
- **Research**: Academic studies on esports performance and trends

## Advanced Usage

### Pagination

Many functions support pagination for large datasets:

```python
import vlrdevapi as vlr

# Get specific page
events = vlr.events.list_events(tier="vct", page=2)

# Limit results
matches = vlr.matches.upcoming(limit=20)

# Combine pagination with limits
results = vlr.matches.completed(limit=50, page=1)
```

### Filtering

Filter data by multiple criteria:

```python
# Filter events by tier and status
vct_events = vlr.events.list_events(
    tier="vct",
    region="na",
    status="ongoing"
)

# Filter player stats by timespan
recent_stats = vlr.players.agent_stats(
    player_id=4164,
    timespan="30d"  # Options: "30d", "60d", "90d", "all"
)
```

### Cache Management

```python
import vlrdevapi as vlr

# Clear cache for fresh data
vlr.fetcher.clear_cache()

# Close connections on shutdown
vlr.fetcher.close_connections()
```

## Error Handling

The library raises specific exceptions for different error cases:

```python
from vlrdevapi.exceptions import NetworkError, RateLimitError

try:
    events = vlr.events.list_events()
except RateLimitError:
    print("Rate limited by VLR.gg")
except NetworkError as e:
    print(f"Network error: {e}")
```

## Testing

The library includes comprehensive tests with real HTML fixtures:

```bash
# Run all tests
pytest tests/lib/

# Run with coverage
pytest tests/lib/ --cov=vlrdevapi

# Run specific test module
pytest tests/lib/test_events.py -v
```

## Documentation and Resources

### Official Documentation

- **[Complete API Reference](https://vlrdevapi.readthedocs.io/)** - Full function and model documentation
- **[Usage Examples](https://vlrdevapi.readthedocs.io/en/latest/examples.html)** - Practical code examples
- **[Data Models](https://vlrdevapi.readthedocs.io/en/latest/models.html)** - Model schemas and validation
- **[Installation Guide](https://vlrdevapi.readthedocs.io/en/latest/installation.html)** - Setup and troubleshooting

### Community and Support

- **GitHub**: [github.com/vanshbordia/vlrdevapi](https://github.com/vanshbordia/vlrdevapi)
- **Issues**: [Report bugs or request features](https://github.com/vanshbordia/vlrdevapi/issues)
- **Discussions**: [Community Q&A](https://github.com/vanshbordia/vlrdevapi/discussions)

## Frequently Asked Questions

### Is this an official VLR.gg API?

No. VLR.gg does not provide an official API. vlrdevapi is a community-maintained web scraping library that provides programmatic access to publicly available data on VLR.gg.

### Is web scraping legal?

vlrdevapi only accesses publicly available data and respects VLR.gg's servers with built-in rate limiting, caching, and retry logic. Always use the library responsibly.

### What Python versions are supported?

Python 3.11 and higher. The library uses modern Python features including type hints and pattern matching.

### How do I get player/event IDs?

IDs can be found in VLR.gg URLs. For example, in `https://www.vlr.gg/player/4164/aspas`, the player ID is `4164`.

### Does it support other games?

No. vlrdevapi is specifically designed for Valorant esports data from VLR.gg.

## Project Structure

```
vlrdevapi/
├── src/vlrdevapi/          # Source code
│   ├── events.py           # Events API
│   ├── matches.py          # Matches API
│   ├── players.py          # Players API
│   ├── series.py           # Series API
│   ├── fetcher.py          # HTTP client
│   ├── utils.py            # Parsing utilities
│   ├── exceptions.py       # Custom exceptions
│   └── constants.py        # Configuration
├── tests/                  # Test suite
│   ├── lib/                # Library tests
│   └── html_sources/       # HTML fixtures
├── docs/                   # Documentation
└── pyproject.toml          # Package configuration
```

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest tests/lib/`
2. Code follows project style
3. New features include tests and documentation

## License

Released under the MIT License. See LICENSE for details.


## Disclaimer

This library scrapes data from VLR.gg. Please use responsibly and respect their terms of service. The library includes rate limiting protection and caching to minimize server load. vlrdevapi is not affiliated with or endorsed by VLR.gg or Riot Games.

## Version

Current version: **1.0.0**
