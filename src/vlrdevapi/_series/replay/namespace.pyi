import httpx

from vlrdevapi._series.replay.models import ReplayData
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesReplayNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: object = ...,
    ) -> None: ...

    def __call__(self, series_id: int, game_id: int) -> ReplayData:
        ...
