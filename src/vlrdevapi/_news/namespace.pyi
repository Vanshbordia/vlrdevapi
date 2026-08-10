from typing import Literal

import httpx

from vlrdevapi.fetcher import RateLimiter, RetryConfig


class NewsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...
    
    @property
    def news(self) -> NewsNamespace: ...