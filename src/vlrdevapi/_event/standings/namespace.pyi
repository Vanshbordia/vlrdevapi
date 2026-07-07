from vlrdevapi._event.standings.models import EventStandings
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class EventStandingsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, event_id: int, stage: str | None = None) -> EventStandings:
        ...
