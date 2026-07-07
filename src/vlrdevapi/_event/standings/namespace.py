"""Event standings namespace — fetches and parses standings per stage."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event._common import _filter_stages
from vlrdevapi._event.standings.models import EventStageStandings, EventStandings
from vlrdevapi._event.standings.parser import parse_standings, parse_subnav
from vlrdevapi._utils.paths import event as event_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventStandingsNamespace:
    """Access event standings from vlr.gg."""

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

    @sanitize_and_validate
    def __call__(self, event_id: int, stage: str | None = None) -> EventStandings:
        """Get standings for an event on vlr.gg, grouped by stage.

        Args:
            event_id: The unique event identifier on vlr.gg.
            stage: Optional stage name or path to filter by (e.g. 'playoffs').

        Returns:
            EventStandings: Standings per stage with team ``name``, ``tag``,
            ``record`` (wins/losses), ``round_diff``, and ``placement`` info.

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.standings(event_id=123)
            >>> result.stages[0].standings[0].team.name
            'FNATIC'

        """
        main_html = self._sync._fetch(event_path(event_id))
        stages = parse_subnav(main_html)

        if not stages:
            standings = parse_standings(main_html)
            if standings:
                return EventStandings(
                    stages=[
                        EventStageStandings(
                            stage_path="",
                            stage_name="All Stages",
                            standings=standings,
                        ),
                    ],
                )
            return EventStandings(stages=[])

        filtered = _filter_stages(stages, stage)
        hrefs = [href for href, _ in filtered]
        stage_htmls = self._sync._parallel_fetch(hrefs, max_workers=5)

        event_standings = []
        for (href, stage_name), stage_html in zip(filtered, stage_htmls):
            standings = parse_standings(stage_html)
            if standings:
                event_standings.append(
                    EventStageStandings(
                        stage_path=href,
                        stage_name=stage_name,
                        standings=standings,
                    ),
                )

        return EventStandings(stages=event_standings)


