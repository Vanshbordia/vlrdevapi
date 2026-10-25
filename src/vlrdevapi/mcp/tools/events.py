"""Tournament and event tools (brackets, stages, teams, matches)."""

from __future__ import annotations

from typing import Literal

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_events_tools(server: MCPServer) -> None:
    """Register tournament and event-related tools."""

    @server.tool()
    @handle_errors
    def event_info(event_id: int) -> str:
        """Get tournament details (dates, prize pool, location, tier) by VLR event ID.

        Args:
            event_id: Unique VLR.gg event/tournament ID.
        """
        return vlrdevapi.event(event_id).info()

    @server.tool()
    @handle_errors
    def event_stages(event_id: int) -> str:
        """Get stages within a tournament (e.g. Group Stage, Upper Bracket, Playoffs).

        Args:
            event_id: Unique VLR.gg event ID.
        """
        return vlrdevapi.event(event_id).stages()

    @server.tool()
    @handle_errors
    def event_teams(event_id: int, stage: str | None = None) -> str:
        """Get participating teams in a tournament, optionally filtered by stage.

        Args:
            event_id: Unique VLR.gg event ID.
            stage: Optional stage name or slug (e.g. 'playoffs').
        """
        return vlrdevapi.event(event_id).teams(stage=stage)

    @server.tool()
    @handle_errors
    def event_matches(
        event_id: int,
        stage: str | None = None,
        state: Literal["all", "upcoming", "completed"] = "all",
    ) -> str:
        """Get matches scheduled or completed within a tournament.

        Args:
            event_id: Unique VLR.gg event ID.
            stage: Optional stage name or slug to filter.
            state: Match status filter: 'all', 'upcoming', or 'completed'.
        """
        return vlrdevapi.event(event_id).matches(stage=stage, state=state)

    @server.tool()
    @handle_errors
    def event_standings(event_id: int, stage: str | None = None) -> str:
        """Get tournament bracket standings and placements.

        Args:
            event_id: Unique VLR.gg event ID.
            stage: Optional stage name or slug.
        """
        return vlrdevapi.event(event_id).standings(stage=stage)

    @server.tool()
    @handle_errors
    def events_list(
        page: int = 1,
        tier: str = "all",
        region: str = "all",
        status: str | None = None,
    ) -> str:
        """Browse tournament listings filtered by tier, region, and status.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            tier: Event tier filter (e.g. 'all', 'vct', 'gc', 'challengers').
            region: Region filter (e.g. 'all', 'na', 'eu', 'ap', 'sa', 'oceania').
            status: Status filter: 'all', 'ongoing', 'upcoming', or 'completed'.
        """
        return vlrdevapi.event.list(page=page, tier=tier, region=region, status=status)  # type: ignore[arg-type]
