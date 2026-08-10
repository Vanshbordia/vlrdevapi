"""News namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._news.models import NewsPage
from vlrdevapi._news.parser import parse_news_page
from vlrdevapi._utils.paths import NEWS
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class NewsNamespace:
    """Access news listings from vlr.gg."""

    __slots__ = ("_source_tz", "_sync")

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
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, page: int = 1) -> NewsPage:
        """Get news from vlr.gg.

        Args:
            page: Page number (1-indexed).

        Returns:
            NewsPage: An object with ``news`` (list of ``News``, each with
            ``title``, ``subtitle``, ``link``, ``country_name``, ``date``,
            and ``author``) and ``has_next_page``.

        Raises:
            ValidationError: If ``page`` is not a valid positive integer.
            NotFoundError: If the page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.news(page=1)
            >>> result.news[0].title
            'Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins'

        """
        url = NEWS if page == 1 else f"{NEWS}/?page={page}"
        html = self._sync._fetch(url)
        return parse_news_page(html)
