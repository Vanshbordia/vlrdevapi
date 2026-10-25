"""Match listing tools for upcoming, live, and completed matches."""

from __future__ import annotations

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_matches_tools(server: MCPServer) -> None:
    """Register match listing tools."""

    @server.tool()
    @handle_errors
    def matches_upcoming(page: int = 1, max_page: int = 0, return_all: bool = False) -> str:
        """Fetch upcoming pro Valorant matches and tournaments from VLR.gg.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            max_page: Maximum pages to fetch when return_all is True. 0 means unlimited.
            return_all: If True, recursively fetches and aggregates all pages.
        """
        return vlrdevapi.matches.upcoming(page=page, max_page=max_page, return_all=return_all)

    @server.tool()
    @handle_errors
    def matches_live() -> str:
        """Fetch currently live Valorant esports matches with ongoing scores and status."""
        return vlrdevapi.matches.live()

    @server.tool()
    @handle_errors
    def matches_completed(page: int = 1, max_page: int = 0, return_all: bool = False) -> str:
        """Fetch recently completed Valorant match results and scores from VLR.gg.

        Args:
            page: Page number (1-indexed). Defaults to 1.
            max_page: Maximum pages to fetch when return_all is True. 0 means unlimited.
            return_all: If True, recursively fetches and aggregates all pages.
        """
        return vlrdevapi.matches.completed(page=page, max_page=max_page, return_all=return_all)
