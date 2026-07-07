"""Top-level event namespace with curried access pattern."""

from typing import Literal

import httpx

from vlrdevapi._event.info.models import EventInfo
from vlrdevapi._event.info.namespace import EventInfoNamespace
from vlrdevapi._event.list.namespace import EventListNamespace
from vlrdevapi._event.matches.models import EventMatches
from vlrdevapi._event.matches.namespace import EventMatchesNamespace
from vlrdevapi._event.stages.models import EventStages
from vlrdevapi._event.stages.namespace import EventStagesNamespace
from vlrdevapi._event.standings.models import EventStandings
from vlrdevapi._event.standings.namespace import EventStandingsNamespace
from vlrdevapi._event.teams.models import EventTeams
from vlrdevapi._event.teams.namespace import EventTeamsNamespace
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class EventMatchNamespace:
    """Curried namespace with a pre-bound event_id.

    Created by calling ``vlrdevapi.event(event_id)``. Call methods
    like ``.info()``, ``.stages()``, ``.matches()`` to fetch data
    for that specific event without passing the event_id each time.
    """

    def __init__(
        self,
        event_id: int,
        info: EventInfoNamespace,
        stages: EventStagesNamespace,
        teams: EventTeamsNamespace,
        matches: EventMatchesNamespace,
        standings: EventStandingsNamespace,
    ):
        self._event_id = event_id
        self._info = info
        self._stages = stages
        self._teams = teams
        self._matches = matches
        self._standings = standings

    @sanitize_and_validate
    def info(self) -> EventInfo:
        """Get general info for this event.

        Returns:
            Event details including name, dates, location, prize pool, and tier.

        Raises:
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> ns.info().name
            'VCT Masters Tokyo'

        """
        return self._info(self._event_id)

    @sanitize_and_validate
    def stages(self) -> EventStages:
        """Get stage information for this event.

        Returns:
            Event stages with date ranges (when available).

        Raises:
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> ns.stages().stages[0].name
            'Group Stage'

        """
        return self._stages(self._event_id)

    @sanitize_and_validate
    def teams(self, stage: str | None = None) -> EventTeams:
        """Get teams participating in this event, grouped by stage.

        Args:
            stage: Optional stage name or path to filter by (e.g. ``"playoffs"``).
                If ``None``, returns teams for all stages.

        Returns:
            EventTeams: Teams grouped by stage, with team ``name``, ``tag``,
            ``logo_url``, and roster info where available.

        Raises:
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> teams = ns.teams(stage="playoffs")
            >>> teams.stages[0].teams[0].name
            'FNATIC'

        """
        return self._teams(self._event_id, stage=stage)

    @sanitize_and_validate
    def matches(self, stage_id: str | None = None, state: Literal["all", "completed", "live", "upcoming"] = "all") -> EventMatches:
        """Get matches for this event, with optional stage and status filters.

        Args:
            stage_id: Optional stage name or path to filter by.
            state: Match status filter.
                - ``"all"`` (default): all matches
                - ``"completed"``: finished matches only
                - ``"live"``: matches in progress
                - ``"upcoming"``: scheduled matches

        Returns:
            Matches with team info, scores, and status indicators.

        Raises:
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> ns.matches(state="upcoming").matches[0].stage
            'Playoffs'

        """
        return self._matches(self._event_id, stage_id=stage_id, state=state)

    @sanitize_and_validate
    def standings(self, stage: str | None = None) -> EventStandings:
        """Get standings for this event, grouped by stage.

        Args:
            stage: Optional stage name or path to filter by (e.g. ``"group_a"``).
                If ``None``, returns standings for all stages.

        Returns:
            Standings tables per stage with team records and placement info.

        Raises:
            NotFoundError: If the event page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> ns.standings(stage="group_a").stages[0].standings[0].team.name
            'FNATIC'

        """
        return self._standings(self._event_id, stage=stage)


class EventNamespace:
    """Top-level namespace for event/tournament data.

    Access sub-namespaces for info, stages, teams, matches, standings,
    and event listings. Use ``vlrdevapi.event(event_id)`` for curried access.

    Quick start::

        info = vlrdevapi.event.info(event_id=123)
        matches = vlrdevapi.event(123).matches(state="upcoming")
        standings = vlrdevapi.event(123).standings(stage="group_a")
        listings = vlrdevapi.event.list(tier="vct", region="emea")
    """

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._info = EventInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._stages = EventStagesNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._teams = EventTeamsNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._matches = EventMatchesNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._standings = EventStandingsNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._list = EventListNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @property
    def info(self) -> EventInfoNamespace:
        """Access event info: name, dates, location, prize pool, tier.

        Usage::

            info = vlrdevapi.event.info(event_id=123)

        Returns:
            An ``EventInfoNamespace`` instance. Call with an ``event_id``
            to fetch and return an ``EventInfo`` model.

        """
        return self._info

    @property
    def stages(self) -> EventStagesNamespace:
        """Access stage information for an event.

        Usage::

            stages = vlrdevapi.event.stages(event_id=123)

        Returns:
            An ``EventStagesNamespace`` instance. Call with an ``event_id``
            to fetch and return an ``EventStages`` model.

        """
        return self._stages

    @property
    def teams(self) -> EventTeamsNamespace:
        """Access teams participating in an event.

        Usage::

            teams = vlrdevapi.event.teams(event_id=123, stage="playoffs")

        Returns:
            An ``EventTeamsNamespace`` instance. Call with an ``event_id``
            and optional ``stage`` to return an ``EventTeams`` model.

        """
        return self._teams

    @property
    def matches(self) -> EventMatchesNamespace:
        """Access matches for an event.

        Usage::

            matches = vlrdevapi.event.matches(event_id=123, state="upcoming")

        Returns:
            An ``EventMatchesNamespace`` instance. Call with an ``event_id``
            and optional filters to return an ``EventMatches`` model.

        """
        return self._matches

    @property
    def standings(self) -> EventStandingsNamespace:
        """Access standings for an event.

        Usage::

            standings = vlrdevapi.event.standings(event_id=123, stage="group_a")

        Returns:
            An ``EventStandingsNamespace`` instance. Call with an ``event_id``
            and optional ``stage`` to return an ``EventStandings`` model.

        """
        return self._standings

    @property
    def list(self) -> EventListNamespace:
        """Access event listings with optional filters.

        Usage::

            listings = vlrdevapi.event.list(tier="vct", region="emea")

        Returns:
            An ``EventListNamespace`` instance. Call with optional filters
            (``tier``, ``region``, ``status``) to return an ``EventList`` model.

        """
        return self._list

    @sanitize_and_validate
    def __call__(self, event_id: int) -> EventMatchNamespace:
        """Create a curried namespace bound to a specific event.

        All subsequent calls on the returned object use ``event_id``
        automatically without needing to pass it each time.

        Args:
            event_id: The unique event identifier on vlr.gg.

        Returns:
            EventMatchNamespace: A namespace object with methods ``.info()``,
            ``.stages()``, ``.teams()``, ``.matches()``, and
            ``.standings()`` — all pre-bound to the given ``event_id``.

        Raises:
            ValidationError: If ``event_id`` is not a valid positive integer.

        Examples:
            >>> ns = vlrdevapi.event(123)
            >>> ns.info().name
            'VCT Masters Tokyo'
            >>> ns.matches(state="upcoming").matches[0].stage
            'Playoffs'

        """
        return EventMatchNamespace(
            event_id=event_id,
            info=self._info,
            stages=self._stages,
            teams=self._teams,
            matches=self._matches,
            standings=self._standings,
        )
