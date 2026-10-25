"""Player statistics, roster history, and agent performance tools."""

from __future__ import annotations

from typing import Literal

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_players_tools(server: MCPServer) -> None:
    """Register player-related tools."""

    @server.tool()
    @handle_errors
    def player_info(player_id: int) -> str:
        """Get pro player profile info (IGN, real name, country, social links) by VLR player ID.

        Args:
            player_id: Unique VLR.gg player ID (e.g. 11225).
        """
        return vlrdevapi.player(player_id).info()

    @server.tool()
    @handle_errors
    def player_teams(player_id: int) -> str:
        """Get current and historical teams for a player.

        Args:
            player_id: Unique VLR.gg player ID.
        """
        return vlrdevapi.player(player_id).teams()

    @server.tool()
    @handle_errors
    def player_agents(player_id: int, timespan: Literal["30d", "60d", "90d", "all"] = "all") -> str:
        """Get agent pick rates, win rates, and stats for a player over a time window.

        Args:
            player_id: Unique VLR.gg player ID.
            timespan: Time window for stats: '30d', '60d', '90d', or 'all'.
        """
        return vlrdevapi.player(player_id).agents(timespan=timespan)

    @server.tool()
    @handle_errors
    def player_matches(player_id: int, limit: int = 50) -> str:
        """Get match history for a specific player.

        Args:
            player_id: Unique VLR.gg player ID.
            limit: Maximum number of matches to return (default 50).
        """
        return vlrdevapi.player(player_id).matches(limit=limit)

    @server.tool()
    @handle_errors
    def player_profile(player_id: int) -> str:
        """Get consolidated career overview for a player.

        Args:
            player_id: Unique VLR.gg player ID.
        """
        return vlrdevapi.player(player_id).profile()

    @server.tool()
    @handle_errors
    def player_placements(player_id: int) -> str:
        """Get tournament placements and total prize earnings for a player.

        Args:
            player_id: Unique VLR.gg player ID.
        """
        return vlrdevapi.player(player_id).placements()
