"""Event stages namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event.stages.models import EventStages
from vlrdevapi._event.stages.parser import (
    merge_dates_into_stages,
    parse_event_page_dates,
    parse_event_stages,
)
from vlrdevapi._utils.paths import event as event_path
from vlrdevapi._utils.paths import event_matches
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventStagesNamespace:
    """Access event stages from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, event_id: int) -> EventStages:
        """Get stages for an event on vlr.gg.

        Args:
            event_id: The unique event identifier on vlr.gg.

        Returns:
            EventStages: Stage information including ``stages`` (a list with
            ``name``, ``path``, ``date_range``, and ``is_active`` for each stage).

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.stages(event_id=123)
            >>> result.stages[0].name
            'Group Stage'
            >>> result.stages[0].date_range
            'Feb 14 - 25'

        """
        html = self._sync._fetch(event_matches(event_id))
        result = parse_event_stages(html, event_id)

        if result.stages:
            event_html = self._sync._fetch(event_path(event_id))
            dates_map = parse_event_page_dates(event_html)
            merge_dates_into_stages(result, dates_map)

        return result

