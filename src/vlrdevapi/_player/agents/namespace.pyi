from datetime import tzinfo
from typing import Literal
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._player.agents.models import AgentStatsPage
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class AgentsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ) -> None: ...

    def __call__(
        self,
        player_id: int,
        timespan: Literal["30d", "60d", "90d", "all"] = "all",
    ) -> AgentStatsPage:
        ...
