from vlrdevapi._matches.live.models import LiveMatchesPage
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class LiveMatchesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self) -> LiveMatchesPage:
        ...
