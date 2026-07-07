from vlrdevapi._team.placements.models import TeamPlacements
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class TeamPlacementsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def __call__(self, team_id: int) -> TeamPlacements:
        ...
