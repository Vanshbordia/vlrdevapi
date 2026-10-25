---
icon: lucide/bot
title: MCP Server
description: Model Context Protocol (MCP) server for VLRdevAPI, exposing 41 tools for Claude Desktop, Cursor, Zed, and AI coding assistants.
---

# MCP Server

VLRdevAPI includes a native Model Context Protocol (MCP) server that exposes Valorant esports data to LLM applications and AI coding agents over standard `stdio`.

## CLI Usage

Install the MCP extras:

```bash
pip install "vlrdevapi[mcp]"
```

Run the server via CLI:

```bash
vlrdevapi-mcp
```

Or run directly with `uvx`:

```bash
uvx --from "vlrdevapi[mcp]" vlrdevapi-mcp
```

## Programmatic Usage

::: vlrdevapi.mcp.server.create_server

## Server Tools

The MCP server exposes 41 tools covering:
- **Matches**: `matches_upcoming`, `matches_live`, `matches_completed`
- **Series**: `series_info`, `series_players`, `series_rounds`, `series_performance`, `series_economy`, `series_replay`, `series_vods`, `series_map_summary`
- **Teams**: `team_info`, `team_roster`, `team_stats`, `team_completed_matches`, `team_upcoming_matches`, `team_transactions`, `team_placements`
- **Players**: `player_info`, `player_teams`, `player_agents`, `player_matches`, `player_profile`, `player_placements`
- **Events**: `events_list`, `event_info`, `event_stages`, `event_teams`, `event_matches`, `event_standings`
- **News**: `news_list`, `news_article`
- **Composite Analysis**: `get_match_full_context`, `get_team_overview`, `compare_teams`, `get_player_career_summary`, `get_h2h_matchup`, `get_tournament_dossier`, `get_live_and_upcoming_schedule`, `get_news_digest`
