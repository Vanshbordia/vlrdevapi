from typing import Literal

from vlrdevapi._event.matches.models import EventMatches
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class EventMatchesNamespace:
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
        event_id: int,
        stage_id: str | None = None,
        state: Literal["all", "completed", "live", "upcoming"] = "all",
    ) -> EventMatches:
        ...
