"""Registry for all MCP tools across endpoints and workflows."""

from __future__ import annotations

from vlrdevapi.mcp._common import MCPServer
from vlrdevapi.mcp.tools.composite import register_composite_tools
from vlrdevapi.mcp.tools.events import register_events_tools
from vlrdevapi.mcp.tools.matches import register_matches_tools
from vlrdevapi.mcp.tools.news import register_news_tools
from vlrdevapi.mcp.tools.players import register_players_tools
from vlrdevapi.mcp.tools.series import register_series_tools
from vlrdevapi.mcp.tools.teams import register_teams_tools


def register_all_tools(server: MCPServer) -> None:
    """Register all available tools onto the given MCPServer instance."""
    register_matches_tools(server)
    register_series_tools(server)
    register_teams_tools(server)
    register_players_tools(server)
    register_events_tools(server)
    register_news_tools(server)
    register_composite_tools(server)


__all__ = [
    "register_all_tools",
    "register_composite_tools",
    "register_events_tools",
    "register_matches_tools",
    "register_news_tools",
    "register_players_tools",
    "register_series_tools",
    "register_teams_tools",
]
