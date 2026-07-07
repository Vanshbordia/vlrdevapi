from vlrdevapi._series.economy.models import EconomyData
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesEconomyNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, series_id: int, game_id: int) -> EconomyData:
        ...
