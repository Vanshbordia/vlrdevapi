from vlrdevapi._series.vods.models import SeriesVods
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesVodsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, series_id: int) -> SeriesVods:
        ...
