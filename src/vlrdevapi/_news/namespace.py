"""Top-level news namespace composing listing and article sub-namespaces."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._news.article.models import NewsArticle
from vlrdevapi._news.article.namespace import NewsArticleNamespace
from vlrdevapi._news.list.models import NewsPage
from vlrdevapi._news.list.namespace import NewsListNamespace
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class NewsNamespace:
    """Top-level namespace for news data from vlr.gg.

    Two ways to use it::

        # Browse the news listing (callable)
        page = vlrdevapi.news(page=1)

        # Fetch a single article
        article = vlrdevapi.news.article(734100)

    Quick start::

        page = vlrdevapi.news(page=1)
        first = vlrdevapi.news.article(page.news[0].id)
        print(first.title)
        print(first.content_md)
    """

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ):
        self._source_tz = source_tz
        self._list = NewsListNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._article = NewsArticleNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)

    @sanitize_and_validate
    def __call__(self, page: int = 1) -> NewsPage:
        """Get a page of news from vlr.gg.

        Args:
            page: Page number (1-indexed). Defaults to the first page.

        Returns:
            NewsPage: An object with ``news`` (a list of ``News`` items)
            and ``has_next_page``.

        Raises:
            ValidationError: If ``page`` is not a valid positive integer.
            NotFoundError: If the requested page does not exist.
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.news(page=1)
            >>> result.news[0].title
            'Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins'

        """
        return self._list(page)

    @sanitize_and_validate
    def article(self, article_id: int) -> NewsArticle:
        """Get a single news article from vlr.gg.

        Args:
            article_id: The news article ID (from ``News.id`` or the
                numeric prefix of ``News.link``).

        Returns:
            NewsArticle: The article with ``title``, ``author``, ``date``,
                ``event_name``, ``event_link``, ``content`` (plain text),
                and ``content_md`` (Markdown).

        Raises:
            ValidationError: If ``article_id`` is not a valid positive integer.
            NotFoundError: If the article does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> article = vlrdevapi.news.article(734100)
            >>> article.title
            'Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins'

        """
        return self._article(article_id)
