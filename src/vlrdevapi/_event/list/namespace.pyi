from vlrdevapi._event.list.models import EventList
from vlrdevapi.commons.mappings import RegionType, StatusType, TierType
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class EventListNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    """Access event listings from vlr.gg."""

    def __call__(
        self,
        tier: TierType = "all",
        region: RegionType = "all",
        status: StatusType | None = None,
        page: int = 1,
        max_page: int = 0,
        return_all: bool = False,
    ) -> EventList:
        """Get a list of events from vlr.gg."""
