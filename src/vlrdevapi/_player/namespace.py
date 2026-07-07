"""Top-level player namespace with curried access pattern."""

from datetime import tzinfo
from typing import Literal
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._player.agents.models import AgentStatsPage
from vlrdevapi._player.agents.namespace import AgentsNamespace
from vlrdevapi._player.info.models import PlayerInfo
from vlrdevapi._player.info.namespace import PlayerInfoNamespace
from vlrdevapi._player.matches.models import PlayerMatches
from vlrdevapi._player.matches.namespace import MatchesNamespace
from vlrdevapi._player.profile.models import PlayerProfile
from vlrdevapi._player.profile.namespace import ProfileNamespace
from vlrdevapi._player.teams.models import PlayerTeams
from vlrdevapi._player.teams.namespace import PlayerTeamsNamespace
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class PlayerMatchNamespace:
    """Curried namespace with a pre-bound player_id.

    Created by calling ``vlrdevapi.player(player_id)``. Call methods
    like ``.info()``, ``.teams()``, ``.agents()`` to fetch data
    for that specific player without passing the player_id each time.
    """

    def __init__(
        self,
        player_id: int,
        info: PlayerInfoNamespace,
        teams: PlayerTeamsNamespace,
        agents: AgentsNamespace,
        matches: MatchesNamespace,
        profile: ProfileNamespace,
    ):
        self._player_id = player_id
        self._info = info
        self._teams = teams
        self._agents = agents
        self._matches = matches
        self._profile = profile

    @sanitize_and_validate
    def info(self) -> PlayerInfo:
        """Get basic player info.

        Returns:
            PlayerInfo: Player details including ``name``, ``real_name``,
            ``country``, ``country_code``, ``player_id``, and social media
            links (``twitter``, ``twitch``, ``youtube``).

        Raises:
            ValidationError: If the pre-bound ``player_id`` is not a valid
                positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return self._info(self._player_id)

    @sanitize_and_validate
    def teams(self) -> PlayerTeams:
        """Get current and past teams for this player.

        Returns:
            PlayerTeams: An object with ``current_teams`` (list of
            ``PlayerTeam``) and ``past_teams`` (list of ``PlayerTeam``).
            Each ``PlayerTeam`` has ``name``, ``tag``, and ``team_id``.

        Raises:
            ValidationError: If the pre-bound ``player_id`` is not a valid
                positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return self._teams(self._player_id)

    @sanitize_and_validate
    def agents(self, timespan: Literal["30d", "60d", "90d", "all"] = "all") -> AgentStatsPage:
        """Get agent statistics for this player.

        Args:
            timespan: Time range for stats.
                - ``"30d"``: last 30 days
                - ``"60d"``: last 60 days
                - ``"90d"``: last 90 days
                - ``"all"`` (default): all available data

        Returns:
            AgentStatsPage: An object with ``agents`` (list of
            ``AgentStats``, each with ``name``, ``rounds``, ``wins``,
            ``rating``, ``acs``, ``kd``, and ``adr``) and ``timespan``.

        Raises:
            ValidationError: If the pre-bound ``player_id`` is not a valid
                positive integer or if ``timespan`` is invalid.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return self._agents(self._player_id, timespan=timespan)

    @sanitize_and_validate
    def matches(self, limit: int = 20) -> PlayerMatches:
        """Get match history for this player.

        Args:
            limit: Maximum number of matches to return (default 20).

        Returns:
            PlayerMatches: An object with ``player_id`` and ``matches``
            (list of ``MatchEntry``, each with ``teams``, ``score``,
            ``map``, ``event``, ``round``, and ``result``).

        Raises:
            ValidationError: If the pre-bound ``player_id`` is not a valid
                positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return self._matches(self._player_id, limit=limit)

    @sanitize_and_validate
    def profile(self) -> PlayerProfile:
        """Get full consolidated profile for this player.

        Returns:
            PlayerProfile: An object with ``name``, ``real_name``,
            ``country``, ``country_code``, ``player_id``, ``twitter``,
            ``twitch``, ``youtube``, ``current_team``, ``top_agents``,
            and ``aliases``.

        Raises:
            ValidationError: If the pre-bound ``player_id`` is not a valid
                positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return self._profile(self._player_id)


class PlayerNamespace:
    """Top-level namespace for player data.

    Access sub-namespaces for info, teams, agents, match history, and
    consolidated profiles. Use ``vlrdevapi.player(player_id)`` for
    curried access.

    Quick start::

        info = vlrdevapi.player.info(player_id=11225)
        matches = vlrdevapi.player(11225).matches(limit=20)
        agents = vlrdevapi.player(11225).agents(timespan="60d")
        profile = vlrdevapi.player(11225).profile()
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
        self._info = PlayerInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._teams = PlayerTeamsNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._agents = AgentsNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._matches = MatchesNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)
        self._profile = ProfileNamespace(client, timeout, retry_config, rate_limiter, extra_headers, source_tz=source_tz)

    @property
    def info(self) -> PlayerInfoNamespace:
        """Access basic player info.

        Usage::

            info = vlrdevapi.player.info(player_id=11225)

        Returns:
            PlayerInfoNamespace: A namespace instance. Call with a ``player_id``
            to fetch and return a ``PlayerInfo`` model.

        """
        return self._info

    @property
    def teams(self) -> PlayerTeamsNamespace:
        """Access current and past teams for a player.

        Usage::

            teams = vlrdevapi.player.teams(player_id=11225)

        Returns:
            PlayerTeamsNamespace: A namespace instance. Call with a ``player_id``
            to fetch and return a ``PlayerTeams`` model.

        """
        return self._teams

    @property
    def agents(self) -> AgentsNamespace:
        """Access agent statistics for a player.

        Usage::

            agents = vlrdevapi.player.agents(player_id=11225, timespan="60d")

        Returns:
            AgentsNamespace: A namespace instance. Call with a ``player_id``
            and optional ``timespan`` to return an ``AgentStatsPage`` model.

        """
        return self._agents

    @property
    def matches(self) -> "MatchesNamespace":
        """Access match history for a player.

        Usage::

            matches = vlrdevapi.player.matches(player_id=11225, limit=20)

        Returns:
            MatchesNamespace: A namespace instance. Call with a ``player_id``
            and optional ``limit`` to return a ``PlayerMatches`` model.

        """
        return self._matches

    @property
    def profile(self) -> ProfileNamespace:
        """Access consolidated profile for a player.

        Usage::

            profile = vlrdevapi.player.profile(player_id=11225)

        Returns:
            ProfileNamespace: A namespace instance. Call with a ``player_id``
            to fetch and return a ``PlayerProfile`` model.

        """
        return self._profile

    @sanitize_and_validate
    def __call__(self, player_id: int) -> PlayerMatchNamespace:
        """Create a curried namespace bound to a specific player.

        All subsequent calls on the returned object use ``player_id``
        automatically without needing to pass it each time.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerMatchNamespace: A namespace object with methods ``.info()``,
            ``.teams()``, ``.agents()``, ``.matches()``, and
            ``.profile()`` — all pre-bound to the given ``player_id``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.

        Examples:
            >>> ns = vlrdevapi.player(11225)
            >>> ns.info().name
            'zekken'
            >>> ns.agents(timespan="60d").agents[0].name
            'Raze'

        """
        return PlayerMatchNamespace(
            player_id=player_id,
            info=self._info,
            teams=self._teams,
            agents=self._agents,
            matches=self._matches,
            profile=self._profile,
        )



