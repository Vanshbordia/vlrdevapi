"""Event info namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event.info.models import EventInfo
from vlrdevapi._event.info.parser import parse_event_info
from vlrdevapi._utils.paths import event as event_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventInfoNamespace:
    """Access event info from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    def _sync_get(self, event_id: int) -> EventInfo:
        """Fetch event info synchronously.

        Args:
            event_id: The unique event identifier on vlr.gg.

        Returns:
            EventInfo with parsed event details.

        """
        return self(event_id)

    @sanitize_and_validate
    def __call__(self, event_id: int) -> EventInfo:
        """Get info for an event on vlr.gg.

        Args:
            event_id: The unique event identifier on vlr.gg.

        Returns:
            EventInfo: Event details including ``name``, ``tier``, ``region``,
            ``dates``, ``prize_pool``, ``location``, ``teams``, and
            ``status`` (ongoing/upcoming/completed).

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.info(event_id=123)
            >>> result.name
            'VCT Masters Tokyo'
            >>> result.tier
            'vct'

        """
        html = self._sync._fetch(event_path(event_id))
        return parse_event_info(html, event_id)

