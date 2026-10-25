"""Model Context Protocol (MCP) server for vlrdevapi.

Exposes comprehensive Valorant esports data tools from VLR.gg to LLM agents
(Claude Desktop, Cursor, Windsurf, etc.) over stdio transport.
"""

from __future__ import annotations

from vlrdevapi.mcp._common import MCPServer
from vlrdevapi.mcp.tools import register_all_tools


def create_server() -> MCPServer:
    """Construct and configure the vlrdevapi MCP server with all tools registered."""
    server = MCPServer(
        "vlrdevapi",
        description=(
            "Query VLR.gg Valorant esports data: matches, tournaments, "
            "players, teams, economy, and replay timelines."
        ),
    )
    register_all_tools(server)
    return server


def main() -> None:
    """CLI entrypoint to run the vlrdevapi MCP server via stdio transport."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
