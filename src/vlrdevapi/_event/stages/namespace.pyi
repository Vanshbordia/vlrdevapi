from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._event.stages.models import EventStages
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class EventStagesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ) -> None: ...

    def __call__(self, event_id: int) -> EventStages:
        ...
