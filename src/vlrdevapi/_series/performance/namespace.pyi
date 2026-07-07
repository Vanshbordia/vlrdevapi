from vlrdevapi._series.performance.models import PerformanceData
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesPerformanceNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, series_id: int, game_id: int | str = "all") -> PerformanceData:
        ...
