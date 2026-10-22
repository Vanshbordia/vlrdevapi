from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._series.players.models import PlayersStats
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesPlayersNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ) -> None: ...

    def __call__(self, series_id: int, game_id: int | str = "all") -> PlayersStats:
        ...
