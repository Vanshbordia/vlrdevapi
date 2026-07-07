"""Synchronous HTTP client for vlr.gg."""

import logging
from datetime import tzinfo
from typing import Any
from zoneinfo import ZoneInfo

__all__ = ["VLRClient"]

import httpx

from vlrdevapi.commons.timezone import REFERENCE_MATCH_PATH, detect_vlr_timezone
from vlrdevapi._event.namespace import EventNamespace
from vlrdevapi._matches.namespace import MatchesNamespace
from vlrdevapi._player.namespace import PlayerNamespace
from vlrdevapi._series.namespace import SeriesNamespace
from vlrdevapi._team.namespace import TeamNamespace
from vlrdevapi.exceptions import HTTPError, NotFoundError, RateLimitError, RequestError
from vlrdevapi.fetcher import (
    BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_RATE_LIMIT,
    DEFAULT_TIMEOUT,
    BackoffStrategy,
    RateLimiter,
    RetryConfig,
    fetch_sync,
)

logger = logging.getLogger(__name__)


class VLRClient:
    """Synchronous client for scraping data from vlr.gg.

    Provides access to namespace attributes for players, series, matches,
    teams, and events.

    Examples:
        >>> with VLRClient() as client:
        ...     info = client.series.info(series_id=1)

        >>> client = VLRClient(max_retries=5, base_delay=2.0,
        ...     backoff=BackoffStrategy.LINEAR)

        >>> client = VLRClient(requests_per_second=2.0)

    Args:
        base_url: Base URL for vlr.gg. Defaults to ``"https://www.vlr.gg"``.
        headers: Additional HTTP headers to merge with defaults.
        timeout: Request timeout in seconds. Defaults to ``15``.
        max_retries: Maximum number of retry attempts after the initial request.
            Defaults to ``3`` (4 total attempts).
        base_delay: Base delay in seconds between retries. The actual delay
            depends on the ``backoff`` strategy. Defaults to ``1.0``.
        backoff: Backoff strategy for calculating delay between retries.
            Defaults to ``BackoffStrategy.EXPONENTIAL``.
        requests_per_second: Rate limit in requests per second. ``0`` means
            unlimited. Defaults to ``3``.
        source_tz: Timezone VLR.gg uses to render datetimes for this client.
            When ``None``, datetimes fall back to UTC unless
            ``auto_detect_tz`` is enabled.
        auto_detect_tz: When ``True`` and ``source_tz`` is not provided, fetch
            a reference match on init to detect the viewer timezone. Defaults
            to ``False`` (opt-in) to avoid a hidden network call in
            ``__init__``.
        **httpx_kwargs: Additional keyword arguments passed to ``httpx.Client``.

    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        headers: dict[str, str] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        requests_per_second: float = DEFAULT_RATE_LIMIT,
        source_tz: str | ZoneInfo | tzinfo | None = None,
        auto_detect_tz: bool = False,
        **httpx_kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_config = RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            backoff=backoff,
        )
        self._rate_limiter = RateLimiter(requests_per_second) if requests_per_second > 0 else None
        merged_headers = {**DEFAULT_HEADERS, **(headers or {})}

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=merged_headers,
            follow_redirects=True,
            **httpx_kwargs,
        )

        if isinstance(source_tz, str):
            self._source_tz: ZoneInfo | tzinfo | None = ZoneInfo(source_tz)
        else:
            self._source_tz = source_tz

        if self._source_tz is None and auto_detect_tz:
            self._source_tz = self._detect_timezone()

        self.player = PlayerNamespace(self._client, self.timeout, self.retry_config, self._rate_limiter, merged_headers, self._source_tz)
        self.series = SeriesNamespace(self._client, self.timeout, self.retry_config, self._rate_limiter, merged_headers, self._source_tz)
        self.matches = MatchesNamespace(self._client, self.timeout, self.retry_config, self._rate_limiter, merged_headers, self._source_tz)
        self.team = TeamNamespace(self._client, self.timeout, self.retry_config, self._rate_limiter, merged_headers, self._source_tz)
        self.event = EventNamespace(self._client, self.timeout, self.retry_config, self._rate_limiter, merged_headers, self._source_tz)

    def _detect_timezone(self) -> ZoneInfo | tzinfo | None:
        """Detect the viewer timezone VLR.gg renders for this client session."""
        try:
            html = fetch_sync(
                self._client,
                REFERENCE_MATCH_PATH,
                self.timeout,
                retry_config=self.retry_config,
                rate_limiter=self._rate_limiter,
            )
            return detect_vlr_timezone(html)
        except (HTTPError, NotFoundError, RateLimitError, RequestError) as exc:
            logger.warning("Failed to auto-detect VLR timezone: %s", exc)
            return None

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> "VLRClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
