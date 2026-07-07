from datetime import date

from vlrdevapi._team.stats.models import AgentCompositionLevel, TeamStats
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class TeamStatsNamespace:
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
        team_id: int,
        date_start: date | None = None,
        date_end: date | None = None,
        event_id: int | None = None,
        series_id: int | None = None,
        subseries_id: int | None = None,
        last_days: int | None = None,
        agent_composition: AgentCompositionLevel = "none",
    ) -> TeamStats:
        ...
