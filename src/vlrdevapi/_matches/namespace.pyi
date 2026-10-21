from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._matches.completed.namespace import CompletedMatchesNamespace
from vlrdevapi._matches.live.namespace import LiveMatchesNamespace
from vlrdevapi._matches.upcoming.namespace import UpcomingMatchesNamespace
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class MatchesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ) -> None: ...

    @property
    def upcoming(self) -> UpcomingMatchesNamespace: ...

    @property
    def live(self) -> LiveMatchesNamespace: ...

    @property
    def completed(self) -> CompletedMatchesNamespace: ...
