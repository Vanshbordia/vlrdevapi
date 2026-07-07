"""Live matches namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._cache import LRUCache
from vlrdevapi._matches.live.models import LiveMatchesPage
from vlrdevapi._matches.live.parser import parse_live_matches
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._utils.paths import MATCHES
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class LiveMatchesNamespace:
    """Access live matches from vlr.gg."""

    __slots__ = ("_series_info", "_sync", "_team_cache")

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._series_info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._team_cache: LRUCache[int, dict[str, str]] = LRUCache[int, dict[str, str]](maxsize=256)

    @sanitize_and_validate
    def __call__(self) -> LiveMatchesPage:
        """Get currently live matches from vlr.gg.

        Returns:
            LiveMatchesPage: An object with ``matches`` (list of
            ``LiveMatch``, each with ``team1``, ``team2``, ``score1``,
            ``score2``, ``event``, and ``round`` information).

        Raises:
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.matches.live()
            >>> result.matches[0].team1
            'Sentinels'

        """
        html = self._sync._fetch(MATCHES)
        return parse_live_matches(
            html, self._series_info, self._sync._client, self._sync._timeout, self._sync._retry_config, self._team_cache,
        )

