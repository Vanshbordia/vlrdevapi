from vlrdevapi._event.info.models import EventInfo
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class EventInfoNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, event_id: int) -> EventInfo:
        ...
