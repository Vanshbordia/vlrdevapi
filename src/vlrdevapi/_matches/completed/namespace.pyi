from vlrdevapi._matches.completed.models import CompletedMatchesPage
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class CompletedMatchesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(
        self,
        page: int = 1,
        max_page: int = 0,
        return_all: bool = False,
    ) -> CompletedMatchesPage:
        ...
