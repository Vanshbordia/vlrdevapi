from vlrdevapi._series.info.models import SeriesInfo
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesInfoNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, series_id: int) -> SeriesInfo:
        ...
