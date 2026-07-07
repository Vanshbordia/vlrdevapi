"""Series info namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.info.models import SeriesInfo
from vlrdevapi._series.info.parser import parse_series_info
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesInfoNamespace:
    """Access series/match overview info from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, series_id: int) -> SeriesInfo:
        """Get overview info for a match/series on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.

        Returns:
            SeriesInfo: Series metadata including ``team1``, ``team2``,
            ``event_name``, ``scores``, ``match_format`` (bo3/bo5),
            ``status``, and ``patch``.

        Raises:
            ValidationError: If ``series_id`` is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.series.info(series_id=12345)
            >>> result.team1.name
            'FNATIC'
            >>> result.event_name
            'VCT LOCK//IN São Paulo'

        """
        html = self._sync._fetch(series_path(series_id))
        result = parse_series_info(html)
        result.series_id = series_id
        return result
