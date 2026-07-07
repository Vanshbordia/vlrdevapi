from vlrdevapi._matches.completed.namespace import CompletedMatchesNamespace
from vlrdevapi._matches.live.namespace import LiveMatchesNamespace
from vlrdevapi._matches.upcoming.namespace import UpcomingMatchesNamespace
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig


class MatchesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def upcoming(self) -> UpcomingMatchesNamespace: ...

    @property
    def live(self) -> LiveMatchesNamespace: ...

    @property
    def completed(self) -> CompletedMatchesNamespace: ...
