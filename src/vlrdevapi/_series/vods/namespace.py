"""Series vods namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.vods.models import SeriesVods
from vlrdevapi._series.vods.parser import parse_series_vods
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesVodsNamespace:
    """Access VOD/video links for a series/match from vlr.gg."""

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
    def __call__(self, series_id: int) -> SeriesVods:
        """Get VOD/video links for a match/series on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.

        Returns:
            SeriesVods: VOD metadata including ``series_id``, ``games``
            (list of ``GameVods`` with ``youtube`` and ``twitch`` URLs
            per game), and ``event_name``.

        Raises:
            ValidationError: If ``series_id`` is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> vods = vlrdevapi.series.vods(series_id=12345)
            >>> vods.games[0].youtube
            'https://www.youtube.com/watch?v=...'
            >>> vods.games[0].twitch
            'https://www.twitch.tv/videos/...'

        """
        html = self._sync._fetch(series_path(series_id))
        result = parse_series_vods(html)
        result.series_id = series_id
        return result

