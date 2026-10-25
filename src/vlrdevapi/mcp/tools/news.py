"""News listings and article tools."""

from __future__ import annotations

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_news_tools(server: MCPServer) -> None:
    """Register news-related tools."""

    @server.tool()
    @handle_errors
    def news_list(page: int = 1) -> str:
        """Browse recent Valorant esports news articles and editorial headlines from VLR.gg.

        Args:
            page: Page number (1-indexed). Defaults to 1.
        """
        return vlrdevapi.news(page=page)

    @server.tool()
    @handle_errors
    def news_article(article_id: int) -> str:
        """Get full article text, author, date, and Markdown content by article ID.

        Args:
            article_id: Unique VLR.gg news article ID.
        """
        return vlrdevapi.news.article(article_id=article_id)
