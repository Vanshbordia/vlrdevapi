"""Unit tests for the MCP server and tool registry."""

from __future__ import annotations

import asyncio
import json
import re
from unittest.mock import patch

import pytest

pytest.importorskip("mcp", reason="mcp optional dependency is required for MCP tests")

from vlrdevapi.exceptions import NotFoundError, ValidationError
from vlrdevapi.mcp.server import create_server


def test_mcp_server_initialization() -> None:
    """Verify that create_server registers the expected tool set."""
    server = create_server()
    assert server.name == "vlrdevapi"

    tools = asyncio.run(server.list_tools())
    tool_names = {t.name for t in tools}

    expected_tools = {
        # Matches
        "matches_upcoming",
        "matches_live",
        "matches_completed",
        # Series
        "series_info",
        "series_players",
        "series_rounds",
        "series_performance",
        "series_economy",
        "series_replay",
        "series_vods",
        # Teams
        "team_info",
        "team_roster",
        "team_stats",
        "team_completed_matches",
        "team_upcoming_matches",
        "team_transactions",
        "team_placements",
        # Players
        "player_info",
        "player_teams",
        "player_agents",
        "player_matches",
        "player_profile",
        "player_placements",
        # Events
        "event_info",
        "event_stages",
        "event_teams",
        "event_matches",
        "event_standings",
        "events_list",
        # News
        "news_list",
        "news_article",
        # Series Map Summary
        "series_map_summary",
        # Composite
        "get_match_full_context",
        "get_team_overview",
        "compare_teams",
        "get_player_career_summary",
        "get_h2h_matchup",
        "get_tournament_dossier",
        "get_live_and_upcoming_schedule",
        "get_news_digest",
    }

    assert expected_tools.issubset(tool_names)


def test_mcp_tool_casing_and_names() -> None:
    """Verify all tool names follow standard MCP conventions (snake_case, <= 64 chars)."""
    server = create_server()
    tools = asyncio.run(server.list_tools())

    name_pattern = re.compile(r"^[a-z0-9_]{1,64}$")

    for tool in tools:
        assert name_pattern.match(tool.name), (
            f"Tool name '{tool.name}' does not match snake_case identifier convention (^[a-z0-9_]{{1,64}}$)"
        )
        assert tool.name == tool.name.lower(), f"Tool name '{tool.name}' must be lowercase"
        assert " " not in tool.name, f"Tool name '{tool.name}' must not contain spaces"
        assert len(tool.name) <= 64, f"Tool name '{tool.name}' exceeds maximum length of 64 characters"


def test_mcp_tool_descriptions_and_schemas() -> None:
    """Verify all tools have non-empty docstrings and valid input schemas."""
    server = create_server()
    tools = asyncio.run(server.list_tools())

    for tool in tools:
        assert tool.description, f"Tool '{tool.name}' is missing a description"
        assert len(tool.description.strip()) > 10, f"Tool '{tool.name}' description is too short"
        # Input schema must be an object schema
        schema = getattr(tool, "input_schema", getattr(tool, "inputSchema", None))
        assert isinstance(schema, dict), f"Tool '{tool.name}' has invalid schema type: {type(schema)}"
        assert schema.get("type") == "object", f"Tool '{tool.name}' schema is not an object"


def test_mcp_error_handling_graceful_json() -> None:
    """Verify that domain errors (NotFoundError, ValidationError) return JSON rather than crashing."""
    server = create_server()

    # Test NotFoundError trapping
    with patch("vlrdevapi.player") as mock_player:
        mock_player.return_value.info.side_effect = NotFoundError("Player with ID 99999999 not found")
        result = asyncio.run(server.call_tool("player_info", {"player_id": 99999999}))
        assert result.content
        payload = json.loads(result.content[0].text)
        assert payload.get("error") == "NotFound"
        assert "not found" in payload.get("message", "")

    # Test ValidationError trapping
    with patch("vlrdevapi.team") as mock_team:
        mock_team.return_value.info.side_effect = ValidationError("Invalid team ID")
        result = asyncio.run(server.call_tool("team_info", {"team_id": -5}))
        assert result.content
        payload = json.loads(result.content[0].text)
        assert payload.get("error") == "ValidationError"


def test_mcp_composite_tool_serialization() -> None:
    """Verify that composite tools return valid serialized JSON strings."""
    server = create_server()

    with patch("vlrdevapi.series") as mock_series:
        mock_match = mock_series.return_value
        mock_match.info.return_value.to_dict.return_value = {"id": 123, "event": "VCT Masters"}
        mock_match.players.return_value.to_dict.return_value = {"players": []}
        mock_match.vods.return_value.to_dict.return_value = {"vods": []}

        result = asyncio.run(server.call_tool("get_match_full_context", {"series_id": 123}))
        assert result.content
        payload = json.loads(result.content[0].text)
        assert "overview" in payload
        assert payload["overview"]["event"] == "VCT Masters"
        assert "player_statistics" in payload
        assert "vods" in payload
