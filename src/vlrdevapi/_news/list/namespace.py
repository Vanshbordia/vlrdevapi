"""News listing namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._news.list.models import NewsPage
from vlrdevapi._news.list.parser import parse_news_page
from vlrdevapi._utils.paths import NEWS
from vlrdevapi.exceptions import NotFoundError
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class NewsListNamespace:
    """Access news listings from vlr.gg.

    Call the instance to fetch a page of news items::

        page = vlrdevapi.news(page=1)
        for item in page.news:
            print(item.title)

    The namespace is reachable via ``vlrdevapi.news``. There is no need
    to instantiate it directly.
    """

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
        self._sync = SyncNamespace(
            client, timeout, retry_config, rate_limiter, extra_headers
        )

    @sanitize_and_validate
    def __call__(self, page: int = 1) -> NewsPage:
        """Get a page of news from vlr.gg.

        Args:
            page: Page number (1-indexed). Defaults to the first page.

        Returns:
            NewsPage: An object with ``news`` (a list of ``News`` items,
            each with ``title``, ``subtitle``, ``link``, ``country_name``,
            ``date``, and ``author``), ``has_next_page``, and
            ``page_number``.

        Raises:
            ValidationError: If ``page`` is not a valid positive integer.
            NotFoundError: If the requested page does not exist (no news
                items are returned for out-of-range pages).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.

        Examples:
            >>> result = vlrdevapi.news(page=1)
            >>> result.news[0].title
            'Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins'
            >>> result.has_next_page
            True

        """
        url = NEWS if page == 1 else f"{NEWS}/?page={page}"
        html = self._sync._fetch(url)
        parsed = parse_news_page(html)
        if not parsed.news:
            msg = f"News page {page} does not exist"
            raise NotFoundError(msg)
        return parsed
