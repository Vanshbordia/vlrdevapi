from vlrdevapi._matches.upcoming.models import UpcomingMatchesPage
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class UpcomingMatchesNamespace:
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
    ) -> UpcomingMatchesPage:
        ...
