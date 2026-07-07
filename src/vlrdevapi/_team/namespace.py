"""Top-level team namespace with curried access pattern."""

from datetime import date, tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._team.completed_matches import TeamCompletedMatchesNamespace
from vlrdevapi._team.completed_matches.models import TeamCompletedMatches
from vlrdevapi._team.info.models import TeamInfo
from vlrdevapi._team.info.namespace import TeamInfoNamespace
from vlrdevapi._team.placements import TeamPlacementsNamespace
from vlrdevapi._team.placements.models import TeamPlacements
from vlrdevapi._team.roster.models import TeamRoster
from vlrdevapi._team.roster.namespace import TeamRosterNamespace
from vlrdevapi._team.stats import TeamStatsNamespace
from vlrdevapi._team.stats.models import AgentCompositionLevel, TeamStats
from vlrdevapi._team.transactions import TeamTransactionsNamespace
from vlrdevapi._team.transactions.models import TeamTransactions
from vlrdevapi._team.upcoming_matches import TeamUpcomingMatchesNamespace
from vlrdevapi._team.upcoming_matches.models import TeamUpcomingMatches
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class TeamMatchNamespace:
    """Curried namespace with a pre-bound team_id.

    Created by calling ``vlrdevapi.team(team_id)``. Call methods
    like ``.info()``, ``.roster()``, ``.stats()`` to fetch data
    for that specific team without passing the team_id each time.
    """

    def __init__(
        self,
        team_id: int,
        info: TeamInfoNamespace,
        roster: TeamRosterNamespace,
        completed_matches: TeamCompletedMatchesNamespace,
        upcoming_matches: TeamUpcomingMatchesNamespace,
        transactions: TeamTransactionsNamespace,
        stats: TeamStatsNamespace,
        placements: TeamPlacementsNamespace,
    ):
        self._team_id = team_id
        self._info = info
        self._roster = roster
        self._completed_matches = completed_matches
        self._upcoming_matches = upcoming_matches
        self._transactions = transactions
        self._stats = stats
        self._placements = placements

    @sanitize_and_validate
    def info(self) -> TeamInfo:
        """Get general info for this team.

        Returns:
            TeamInfo: Team details including ``name``, ``tag``, ``country``,
            ``logo_url``, and social media links (``twitter``, ``twitch``,
            ``youtube``).

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.info().name
            'Sentinels'

        """
        return self._info(self._team_id)

    @sanitize_and_validate
    def roster(self) -> TeamRoster:
        """Get the current roster for this team.

        Returns:
            TeamRoster: Active players and staff including ``player_id``,
            ``ign``, ``real_name``, ``country``, and ``role``.

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> roster = ns.roster()
            >>> roster.players[0].ign
            'TenZ'

        """
        return self._roster(self._team_id)

    @sanitize_and_validate
    def completed_matches(self) -> TeamCompletedMatches:
        """Get completed match history for this team.

        Returns:
            TeamCompletedMatches: Completed matches with ``match_id``,
            ``event_name``, ``opponent``, ``score``, ``rounds_won``,
            ``rounds_lost``, ``stage``, and enrichment data (team IDs,
            series info).

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.completed_matches().matches[0].score
            '2-1'

        """
        return self._completed_matches(self._team_id)

    @sanitize_and_validate
    def upcoming_matches(self) -> TeamUpcomingMatches:
        """Get upcoming matches for this team.

        Returns:
            TeamUpcomingMatches: Upcoming matches with ``match_id``,
            ``event_name``, ``opponent``, ``stage``, ``scheduled_time``,
            and enrichment data (team IDs, series info).

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.upcoming_matches().matches[0].opponent
            '100 Thieves'

        """
        return self._upcoming_matches(self._team_id)

    @sanitize_and_validate
    def transactions(self) -> TeamTransactions:
        """Get roster transactions (joins/leaves) for this team.

        Returns:
            TeamTransactions: Chronological list of ``transactions``
            including ``action`` (Join/Leave/Inactive), ``player`` details,
            ``date``, and ``position``.

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.transactions().transactions[0].action
            'Join'

        """
        return self._transactions(self._team_id)

    @sanitize_and_validate
    def stats(
        self,
        date_start: date | None = None,
        date_end: date | None = None,
        event_id: int | None = None,
        series_id: int | None = None,
        subseries_id: int | None = None,
        last_days: int | None = None,
        agent_composition: AgentCompositionLevel = "none",
    ) -> TeamStats:
        """Get map/agent statistics for this team over a date range.

        Args:
            date_start: Start date for stats (inclusive). Defaults to 30 days ago.
            date_end: End date for stats (inclusive). Defaults to today.
            event_id: Filter stats to a specific event.
            series_id: Filter stats to a specific series.
            subseries_id: Filter stats to a specific sub-series.
            last_days: Shorthand to set date range to the last N days.
            agent_composition: Agent composition detail level.
                ``"none"`` (default), ``"composition"``, or ``"detailed"``.

        Returns:
            TeamStats: Map-level statistics including ``maps``,
            ``rounds_won``, ``rounds_lost``, ``kills``, ``deaths``,
            ``assists``, ``acs``, ``kast``, and per-map agent composition
            data when requested.

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.stats(last_days=90).maps[0].win_rate
            66.7

        """
        return self._stats(
            self._team_id,
            date_start=date_start, date_end=date_end,
            event_id=event_id, series_id=series_id,
            subseries_id=subseries_id, last_days=last_days,
            agent_composition=agent_composition,
        )

    @sanitize_and_validate
    def placements(self) -> TeamPlacements:
        """Get event placement history for this team.

        Returns:
            TeamPlacements: Placement history including ``event_name``,
            ``stage``, ``placement``/``rank``, ``prize``, and
            ``total_winnings``.

        Raises:
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.placements().placements[0].placement
            1

        """
        return self._placements(self._team_id)


class TeamNamespace:
    """Top-level namespace for team data.

    Access sub-namespaces for info, roster, stats, matches, transactions,
    and placements. Use ``vlrdevapi.team(team_id)`` for curried access.

    Quick start::

        info = vlrdevapi.team.info(team_id=4568)
        stats = vlrdevapi.team(4568).stats(last_days=90)
        roster = vlrdevapi.team(4568).roster()
    """

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
        self._info = TeamInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._roster = TeamRosterNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._completed_matches = TeamCompletedMatchesNamespace(
            client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz,
        )
        self._upcoming_matches = TeamUpcomingMatchesNamespace(
            client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz,
        )
        self._transactions = TeamTransactionsNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._stats = TeamStatsNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._placements = TeamPlacementsNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)

    @property
    def info(self) -> TeamInfoNamespace:
        """Access team info: name, tag, country, logos, social links.

        Usage::

            info = vlrdevapi.team.info(team_id=4568)

        Returns:
            A ``TeamInfoNamespace`` instance. Call with a ``team_id``
            to fetch and return a ``TeamInfo`` model.

        """
        return self._info

    @property
    def roster(self) -> TeamRosterNamespace:
        """Access team roster: active players and staff.

        Usage::

            roster = vlrdevapi.team.roster(team_id=4568)

        Returns:
            A ``TeamRosterNamespace`` instance. Call with a ``team_id``
            to fetch and return a ``TeamRoster`` model.

        """
        return self._roster

    @property
    def completed_matches(self) -> TeamCompletedMatchesNamespace:
        """Access completed match history for a team.

        Usage::

            matches = vlrdevapi.team.completed_matches(team_id=4568)

        Returns:
            A ``TeamCompletedMatchesNamespace`` instance. Call with a
            ``team_id`` to fetch and return a ``TeamCompletedMatches`` model.

        """
        return self._completed_matches

    @property
    def upcoming_matches(self) -> TeamUpcomingMatchesNamespace:
        """Access upcoming matches for a team.

        Usage::

            matches = vlrdevapi.team.upcoming_matches(team_id=4568)

        Returns:
            A ``TeamUpcomingMatchesNamespace`` instance. Call with a
            ``team_id`` to fetch and return a ``TeamUpcomingMatches`` model.

        """
        return self._upcoming_matches

    @property
    def transactions(self) -> TeamTransactionsNamespace:
        """Access roster transactions (joins / leaves) for a team.

        Usage::

            txns = vlrdevapi.team.transactions(team_id=4568)

        Returns:
            A ``TeamTransactionsNamespace`` instance. Call with a
            ``team_id`` to fetch and return a ``TeamTransactions`` model.

        """
        return self._transactions

    @property
    def stats(self) -> TeamStatsNamespace:
        """Access map / agent statistics for a team.

        Usage::

            stats = vlrdevapi.team.stats(team_id=4568, last_days=90)

        Returns:
            A ``TeamStatsNamespace`` instance. Call with a ``team_id``
            and optional filters to return a ``TeamStats`` model.

        """
        return self._stats

    @property
    def placements(self) -> TeamPlacementsNamespace:
        """Access event placement history for a team.

        Usage::

            placements = vlrdevapi.team.placements(team_id=4568)

        Returns:
            A ``TeamPlacementsNamespace`` instance. Call with a
            ``team_id`` to fetch and return a ``TeamPlacements`` model.

        """
        return self._placements

    @sanitize_and_validate
    def __call__(self, team_id: int) -> TeamMatchNamespace:
        """Create a curried namespace bound to a specific team.

        All subsequent calls on the returned object use ``team_id``
        automatically without needing to pass it each time.

        Args:
            team_id: The unique team identifier on vlr.gg.

        Returns:
            TeamMatchNamespace: A namespace object with methods ``.info()``,
            ``.roster()``, ``.stats()``, ``.completed_matches()``,
            ``.upcoming_matches()``, ``.transactions()``, and
            ``.placements()`` — all pre-bound to the given ``team_id``.

        Raises:
            ValidationError: If ``team_id`` is not a valid positive integer.

        Examples:
            >>> ns = vlrdevapi.team(4568)
            >>> ns.info().name
            'Sentinels'
            >>> ns.stats(last_days=90).maps[0].win_rate
            66.7

        """
        return TeamMatchNamespace(
            team_id=team_id,
            info=self._info, roster=self._roster,
            completed_matches=self._completed_matches,
            upcoming_matches=self._upcoming_matches,
            transactions=self._transactions,
            stats=self._stats, placements=self._placements,
        )
