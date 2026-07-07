"""Event teams namespace — fetches teams per stage with parallel fetches."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event._common import _filter_stages
from vlrdevapi._event.teams.models import EventStageTeams, EventTeams
from vlrdevapi._event.teams.parser import parse_subnav, parse_teams
from vlrdevapi._utils.paths import event as event_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventTeamsNamespace:
    """Access event teams from vlr.gg."""

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
    def __call__(self, event_id: int, stage: str | None = None) -> EventTeams:
        """Get teams for an event on vlr.gg, grouped by stage.

        Args:
            event_id: The unique event identifier on vlr.gg.
            stage: Optional stage name or path to filter by (e.g. 'playoffs').

        Returns:
            EventTeams: Teams grouped by stage, with team ``name``, ``tag``,
            ``logo_url``, and roster info where available.

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.teams(event_id=123)
            >>> result.stages[0].teams[0].name
            'FNATIC'

        """
        main_html = self._sync._fetch(event_path(event_id))
        stages = parse_subnav(main_html)

        if not stages:
            teams = parse_teams(main_html)
            if teams:
                return EventTeams(
                    stages=[
                        EventStageTeams(stage_path="", stage_name="All Teams", teams=teams),
                    ],
                )
            return EventTeams(stages=[])

        filtered = _filter_stages(stages, stage)
        hrefs = [href for href, _ in filtered]
        stage_htmls = self._sync._parallel_fetch(hrefs, max_workers=5)

        event_teams = []
        for (href, stage_name), stage_html in zip(filtered, stage_htmls):
            teams = parse_teams(stage_html)
            if teams:
                event_teams.append(
                    EventStageTeams(stage_path=href, stage_name=stage_name, teams=teams),
                )

        return EventTeams(stages=event_teams)

