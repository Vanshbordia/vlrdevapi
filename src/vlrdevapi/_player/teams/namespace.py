"""Player teams namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.teams.models import PlayerPastTeams, PlayerTeam, PlayerTeams
from vlrdevapi._player.teams.parser import parse_player_teams
from vlrdevapi._utils.paths import player as player_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class PlayerTeamsNamespace:
    """Access player team information from vlr.gg."""

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
    def current_team(self, player_id: int) -> PlayerTeam | None:
        """Get the player's current team.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerTeam or None: If the player is currently on a team, a
            ``PlayerTeam`` object with fields ``name``, ``tag``, and
            ``team_id``; otherwise ``None``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        result = self._fetch_and_parse(player_id)
        return result.current_teams[0] if result.current_teams else None

    @sanitize_and_validate
    def past_teams(self, player_id: int) -> PlayerPastTeams:
        """Get the player's past teams.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerPastTeams: A wrapper object containing ``past_teams``,
            a list of ``PlayerTeam`` objects, each with ``name``, ``tag``,
            and ``team_id``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        """
        return PlayerPastTeams(past_teams=self._fetch_and_parse(player_id).past_teams)

    @sanitize_and_validate
    def __call__(self, player_id: int) -> PlayerTeams:
        """Get all teams (current + past) for a player.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerTeams: An object with ``current_teams`` (list of
            ``PlayerTeam``) and ``past_teams`` (list of ``PlayerTeam``).
            Each ``PlayerTeam`` has ``name``, ``tag``, and ``team_id``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.teams(player_id=11225)
            >>> result.current_teams[0].name
            'Sentinels'

        """
        return self._fetch_and_parse(player_id)

    def _fetch_and_parse(self, player_id: int) -> PlayerTeams:
        html = self._sync._fetch(player_path(player_id))
        return parse_player_teams(html)
