"""Upcoming matches namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._cache import LRUCache
from vlrdevapi._matches.upcoming.models import UpcomingMatchesPage
from vlrdevapi._matches.upcoming.parser import parse_upcoming_matches
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._utils.pagination import collect_all_pages_sync
from vlrdevapi._utils.paths import MATCHES
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class UpcomingMatchesNamespace:
    """Access upcoming matches from vlr.gg."""

    __slots__ = ("_series_info", "_source_tz", "_sync", "_team_cache")

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
        self._series_info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._team_cache: LRUCache[int, dict[str, str]] = LRUCache[int, dict[str, str]](maxsize=256)

    @sanitize_and_validate
    def __call__(self, page: int = 1, max_page: int = 0, return_all: bool = False) -> UpcomingMatchesPage:
        """Get upcoming matches from vlr.gg.

        Args:
            page: Page number (1-indexed). Ignored when return_all=True.
            max_page: Maximum pages to fetch when return_all=True. 0 means no limit.
            return_all: If True, fetches all pages and returns combined results.

        Returns:
            UpcomingMatchesPage: An object with ``matches`` (list of
            ``UpcomingMatch``, each with ``team1``, ``team2``, ``event``,
            ``round``, and scheduled ``time``).

        Raises:
            ValidationError: If ``page`` or ``max_page`` are not valid
                positive integers.
            NotFoundError: If the page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.matches.upcoming(page=1)
            >>> result.matches[0].team1
            'Sentinels'

        """
        if return_all:
            return collect_all_pages_sync(
                fetch_fn=self._sync._fetch,
                build_url=lambda p: MATCHES if p == 1 else f"{MATCHES}?page={p}",
                parse_fn=parse_upcoming_matches,
                max_page=max_page if max_page > 0 else page,
                parse_extra=(self._series_info, self._sync._client, self._sync._timeout, self._sync._retry_config, self._team_cache, self._source_tz),
            )
        url = MATCHES if page == 1 else f"{MATCHES}?page={page}"
        html = self._sync._fetch(url)
        return parse_upcoming_matches(
            html, self._series_info, self._sync._client, self._sync._timeout, self._sync._retry_config, self._team_cache,
            source_tz=self._source_tz,
        )

