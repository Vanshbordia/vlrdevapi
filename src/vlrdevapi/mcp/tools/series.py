"""Series and match analytics tools (scores, players, economy, replay)."""

from __future__ import annotations

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_series_tools(server: MCPServer) -> None:
    """Register series and match-level tools."""

    @server.tool()
    @handle_errors
    def series_info(series_id: int) -> str:
        """Get overview info for a match/series (teams, scores, maps played, format, patch).

        Args:
            series_id: The unique VLR.gg series identifier (e.g. 542272).
        """
        return vlrdevapi.series(series_id).info()

    @server.tool()
    @handle_errors
    def series_players(series_id: int, game_id: str = "all") -> str:
        """Get player statistics (ACS, K/D, ADR, KAST, HS%) for a match or specific map.

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (e.g. '1', '2') or 'all' for overall series stats.
        """
        target_game = int(game_id) if game_id.isdigit() else game_id
        return vlrdevapi.series(series_id).players(game_id=target_game)

    @server.tool()
    @handle_errors
    def series_rounds(series_id: int, game_id: int = 1) -> str:
        """Get round-by-round breakdown (win type, defuse/plant events, attacking/defending side).

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (1-indexed, e.g. 1 for Map 1). Defaults to 1.
        """
        return vlrdevapi.series(series_id).rounds(game_id=int(game_id))

    @server.tool()
    @handle_errors
    def series_performance(series_id: int, game_id: str = "all") -> str:
        """Get head-to-head kill matrix between opposing players in a match.

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (e.g. '1', '2') or 'all'.
        """
        target_game = int(game_id) if game_id.isdigit() else game_id
        return vlrdevapi.series(series_id).performance(game_id=target_game)

    @server.tool()
    @handle_errors
    def series_economy(series_id: int, game_id: str = "all") -> str:
        """Get team economy matrices per round: buy type (eco/full-buy), loadout value, spent credits, and bank.

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (e.g. '1', '2') or 'all'.
        """
        target_game = int(game_id) if game_id.isdigit() else game_id
        return vlrdevapi.series(series_id).economy(game_id=target_game)

    @server.tool()
    @handle_errors
    def series_replay(series_id: int, game_id: int = 1) -> str:
        """Get 2D kill-feed replay timeline with spatial (x, y) coordinates, angles, and player loadouts.

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (1-indexed, e.g. 1 for Map 1). Defaults to 1.
        """
        return vlrdevapi.series(series_id).replay(game_id=int(game_id))

    @server.tool()
    @handle_errors
    def series_vods(series_id: int) -> str:
        """Get official Twitch and YouTube VOD broadcast links for a series match.

        Args:
            series_id: Unique VLR.gg series ID.
        """
        return vlrdevapi.series(series_id).vods()

    @server.tool()
    @handle_errors
    def series_map_summary(series_id: int, game_id: str) -> str:
        """Get an all-in-one breakdown for a specific map: player stats, round events, and economy.

        Args:
            series_id: Unique VLR.gg series ID.
            game_id: Specific game map number (e.g. '1', '2') or real game ID (e.g. '180437').
        """
        target_game = int(game_id) if game_id.isdigit() else game_id
        match = vlrdevapi.series(series_id)
        return {
            "players": match.players(game_id=target_game).to_dict(orient="model"),
            "rounds": match.rounds(game_id=target_game).to_dict(orient="model"),
            "economy": match.economy(game_id=target_game).to_dict(orient="model"),
        }
