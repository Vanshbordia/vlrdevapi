"""Event matches namespace."""

import logging
from typing import Literal

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event.matches.models import EventMatch, EventMatches
from vlrdevapi._event.matches.parser import parse_event_matches
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._utils.paths import event_matches as event_matches_path
from vlrdevapi.exceptions import VlrdevapiException
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate

logger = logging.getLogger(__name__)


def _enrich_match_teams(match: EventMatch, series_info_ns: SeriesInfoNamespace) -> None:
    """Populate match team IDs by fetching series info.

    Args:
        match: EventMatch whose teams will be enriched in-place.
        series_info_ns: Namespace used to fetch series data for each match.

    Raises:
        VlrdevapiException: If the series fetch or parsing fails.

    """
    try:
        series_info = series_info_ns(match.match_id)
        teams = [t for t in (series_info.team1, series_info.team2) if t is not None]
        for i, series_team in enumerate(teams):
            if i < len(match.teams) and series_team.id:
                match.teams[i].id = series_team.id
    except (VlrdevapiException, AttributeError, KeyError, TypeError, ValueError):
        logger.debug("Failed to enrich teams for match %d", match.match_id)
        raise


class EventMatchesNamespace:
    """Access event matches from vlr.gg."""

    __slots__ = ("_series_info", "_sync")

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._series_info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(
        self,
        event_id: int,
        stage_id: str | None = None,
        state: Literal["all", "completed", "live", "upcoming"] = "all",
    ) -> EventMatches:
        """Get matches for an event on vlr.gg.

        Args:
            event_id: The unique event identifier on vlr.gg.
            stage_id: Optional stage name or path to filter by.
            state: Match status filter ('all', 'completed', 'live', 'upcoming').

        Returns:
            EventMatches: Match data including ``matches`` (a list with
            ``match_id``, ``teams``, ``scores``, ``stage``, ``status``,
            and ``eta`` for each match).

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.event.matches(event_id=123, state="upcoming")
            >>> result.matches[0].stage
            'Playoffs'
            >>> result.matches[0].teams[0].name
            'FNATIC'

        """
        params = []
        series_id = stage_id or "all"
        params.append(f"series_id={series_id}")
        if state and state != "all":
            params.append(f"group={state}")

        query_string = "&".join(params)
        path = f"{event_matches_path(event_id)}/?{query_string}"

        html = self._sync._fetch(path)
        result = parse_event_matches(html, event_id)

        if not result.matches:
            return result

        _timeout = self._sync._timeout
        _rc = self._sync._retry_config
        _rl = self._sync._rate_limiter

        def _do_enrich(match: EventMatch, client: httpx.Client) -> None:
            """Enrich a single match's team IDs via series info."""
            local_series_info = SeriesInfoNamespace(client, _timeout, _rc, _rl)
            _enrich_match_teams(match, local_series_info)

        self._sync._parallel_enrich(result.matches, _do_enrich, max_workers=5)
        return result

