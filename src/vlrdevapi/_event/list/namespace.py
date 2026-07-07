"""Event list namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event.list.models import EventList
from vlrdevapi._event.list.parser import parse_event_list
from vlrdevapi._utils.pagination import collect_all_pages_sync
from vlrdevapi.commons.mappings import (
    REGION_MAPPINGS,
    TIER_MAPPINGS,
    RegionType,
    StatusType,
    TierType,
    resolve_region,
    resolve_tier,
)
from vlrdevapi.exceptions import ValidationError
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventListNamespace:
    """Access event listings from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ):
        self._source_tz = source_tz
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    def _sync_get(
        self,
        tier: TierType = "all",
        region: RegionType = "all",
        status: StatusType | None = None,
        page: int = 1,
        max_page: int = 0,
        return_all: bool = False,
    ) -> EventList:
        """Fetch event listings synchronously.

        Args:
            tier: Tier filter (default 'all').
            region: Region filter (default 'all').
            status: Optional status filter.
            page: Page number (default 1). Ignored when return_all=True.
            max_page: Maximum pages to fetch when return_all=True. 0 means no limit.
            return_all: If True, fetches all pages and returns combined results.

        Returns:
            EventList with matching events.

        """
        return self(tier=tier, region=region, status=status, page=page, max_page=max_page, return_all=return_all)

    @sanitize_and_validate
    def __call__(
        self,
        tier: TierType = "all",
        region: RegionType = "all",
        status: StatusType | None = None,
        page: int = 1,
        max_page: int = 0,
        return_all: bool = False,
    ) -> EventList:
        """Get a list of events from vlr.gg.

        Args:
            tier: Tier filter. One of: all, vct, vcl, t3, gc, collegiate, offseason.
            region: Region filter. One of: all, americas, amer, emea, pacific, pac, china.
            status: Optional status filter. One of: ongoing, upcoming, completed, paused.
                    If None, returns events of all statuses.
            page: Page number (1-indexed). Ignored when return_all=True.
            max_page: Maximum pages to fetch when return_all=True. 0 means no limit.
            return_all: If True, fetches all pages and returns combined results.

        Returns:
            EventList: List of events with ``events`` (each containing ``id``,
            ``name``, ``tier``, ``region``, ``status``, ``dates``, and
            ``prize_pool``), plus the original ``params`` used for the query.

        Raises:
            ValidationError: If ``page`` is not a valid positive integer.
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.list(tier="vct", region="emea")
            >>> result.events[0].name
            'VCT 2025 EMEA'
            >>> result.params["tier"]
            'vct'

        """
        tier_val = resolve_tier(tier)
        region_val = resolve_region(region)
        if page < 1:
            msg = "page must be >= 1"
            raise ValidationError(msg)

        canonical_tier = next(
            (k for k, v in TIER_MAPPINGS.items() if v == tier_val), tier.lower(),
        )
        canonical_region = next(
            (k for k, v in REGION_MAPPINGS.items() if v == region_val), region.lower(),
        )
        filters = {"tier": canonical_tier, "region": canonical_region, "status": status, "page": page}

        if return_all:
            result = collect_all_pages_sync(
                fetch_fn=self._sync._fetch,
                build_url=lambda p: _build_events_path(tier_val, region_val, p),
                parse_fn=parse_event_list,
                max_page=max_page,
                parse_extra=(filters,),
            )
            # collect_all_pages_sync sets .matches but not .events
            result.events = result.matches
            return result

        path = _build_events_path(tier_val, region_val, page)
        html = self._sync._fetch(path)
        return parse_event_list(html, filters)



def _build_events_path(tier_val: str, region_val: str, page: int) -> str:
    """Build the URL path for the events listing page.

    Args:
        tier_val: Resolved tier parameter.
        region_val: Resolved region parameter.
        page: Page number (only included if > 1).

    Returns:
        Path string like '/events/?tier=vct&region=emea' or '/events/' for defaults.

    """
    params = []
    if tier_val:
        params.append(f"tier={tier_val}")
    if region_val:
        params.append(f"region={region_val}")
    if page > 1:
        params.append(f"page={page}")
    query = "&".join(params)
    return f"/events/?{query}" if query else "/events/"
