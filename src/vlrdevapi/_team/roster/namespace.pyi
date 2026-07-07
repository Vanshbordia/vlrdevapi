from vlrdevapi._team.roster.models import TeamRoster
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class TeamRosterNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, team_id: int) -> TeamRoster:
        ...
