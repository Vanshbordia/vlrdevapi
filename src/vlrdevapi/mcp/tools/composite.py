"""Composite / multi-step workflow tools designed specifically for AI agents.

These tools combine multiple lower-level API calls into single rich responses,
saving LLM agent turns, tokens, and round-trips.
"""

from __future__ import annotations

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_composite_tools(server: MCPServer) -> None:
    """Register composite multi-endpoint tools."""

    @server.tool()
    @handle_errors
    def get_match_full_context(series_id: int) -> str:
        """Fetch complete context for a match: overview, scores, player ACS stats, and VODs in a single call.

        Designed for AI analysts to immediately summarize or analyze a match without multiple tool turns.

        Args:
            series_id: Unique VLR.gg series identifier.
        """
        match = vlrdevapi.series(series_id)
        info = match.info()
        players = match.players(game_id="all")
        vods = match.vods()

        return {
            "overview": info.model_dump(),
            "player_statistics": players.model_dump(),
            "vods": vods.model_dump(),
        }

    @server.tool()
    @handle_errors
    def get_team_overview(team_id: int) -> str:
        """Get an all-in-one dossier for a team: info, active roster, upcoming schedule, and placements.

        Args:
            team_id: Unique VLR.gg team identifier.
        """
        team = vlrdevapi.team(team_id)
        info = team.info()
        roster = team.roster()
        upcoming = team.upcoming_matches()
        placements = team.placements()

        return {
            "info": info.model_dump(),
            "roster": roster.model_dump(),
            "upcoming_matches": upcoming.model_dump(),
            "placements": placements.model_dump(),
        }

    @server.tool()
    @handle_errors
    def compare_teams(team_id_1: int, team_id_2: int, last_days: int = 60) -> str:
        """Compare two teams head-to-head: rosters, recent map statistics, and forms.

        Ideal for AI agents analyzing upcoming matchups or generating pre-match reports.

        Args:
            team_id_1: First team VLR ID.
            team_id_2: Second team VLR ID.
            last_days: Days of recent map performance to compare (default 60).
        """
        t1 = vlrdevapi.team(team_id_1)
        t2 = vlrdevapi.team(team_id_2)

        return {
            "team_1": {
                "info": t1.info().model_dump(),
                "roster": t1.roster().model_dump(),
                "stats": t1.stats(last_days=last_days).model_dump(),
            },
            "team_2": {
                "info": t2.info().model_dump(),
                "roster": t2.roster().model_dump(),
                "stats": t2.stats(last_days=last_days).model_dump(),
            },
        }
