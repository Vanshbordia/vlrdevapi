"""Team analytics, roster, matches, and transfer tools."""

from __future__ import annotations

from typing import Literal

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_teams_tools(server: MCPServer) -> None:
    """Register team-related tools."""

    @server.tool()
    @handle_errors
    def team_info(team_id: int) -> str:
        """Get team info (name, tag, country, social links) by VLR team ID (e.g. 2593 for FNATIC).

        Args:
            team_id: Unique VLR.gg team ID.
        """
        return vlrdevapi.team(team_id).info()

    @server.tool()
    @handle_errors
    def team_roster(team_id: int) -> str:
        """Get active player roster, coach, and staff for a team.

        Args:
            team_id: Unique VLR.gg team ID.
        """
        return vlrdevapi.team(team_id).roster()

    @server.tool()
    @handle_errors
    def team_stats(
        team_id: int,
        last_days: int | None = None,
        agent_composition: Literal["none", "basic", "detailed", "composition"] = "none",
    ) -> str:
        """Get map-level statistics, win rates, and agent composition data for a team.

        Args:
            team_id: Unique VLR.gg team ID.
            last_days: Optional filter for recent activity (e.g. 30, 60, 90 days).
            agent_composition: Detail level for agent compositions: 'none', 'basic', or 'detailed'.
        """
        comp = "basic" if agent_composition == "composition" else agent_composition
        return vlrdevapi.team(team_id).stats(last_days=last_days, agent_composition=comp)

    @server.tool()
    @handle_errors
    def team_completed_matches(team_id: int, limit: int = 50, return_all: bool = False) -> str:
        """Get past match history and results for a team.

        Args:
            team_id: Unique VLR.gg team ID.
            limit: Maximum number of completed matches to return (default 50).
            return_all: If True, fetches all completed matches for the team.
        """
        return vlrdevapi.team(team_id).completed_matches(limit=limit, return_all=return_all)

    @server.tool()
    @handle_errors
    def team_upcoming_matches(team_id: int) -> str:
        """Get scheduled upcoming matches for a team.

        Args:
            team_id: Unique VLR.gg team ID.
        """
        return vlrdevapi.team(team_id).upcoming_matches()

    @server.tool()
    @handle_errors
    def team_transactions(team_id: int) -> str:
        """Get roster transactions, player additions, benching, and departures for a team.

        Args:
            team_id: Unique VLR.gg team ID.
        """
        return vlrdevapi.team(team_id).transactions()

    @server.tool()
    @handle_errors
    def team_placements(team_id: int) -> str:
        """Get tournament placements and prize money earnings for a team.

        Args:
            team_id: Unique VLR.gg team ID.
        """
        return vlrdevapi.team(team_id).placements()
