"""Player profile namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.profile.models import PlayerProfile
from vlrdevapi._player.profile.parser import parse_player_profile
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class ProfileNamespace:
    """Access a consolidated player profile from vlr.gg."""

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
    def __call__(self, player_id: int) -> PlayerProfile:
        """Get a consolidated player profile summary.

        Fetches player info, current team, and most-played agent stats.
        Tries the ``30d`` timespan first; if no agent stats are found,
        falls back to ``all`` time.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerProfile: An object with ``name``, ``real_name``,
            ``country``, ``country_code``, ``player_id``, ``twitter``,
            ``twitch``, ``youtube``, ``current_team``, ``top_agents``,
            and ``aliases``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.profile(player_id=11225)
            >>> result.name
            'zekken'
            >>> result.current_team
            'Sentinels'

        """
        html = self._sync._fetch(_build_path(player_id, "30d"))
        profile = parse_player_profile(html, timespan="30d")
        profile.player_id = player_id
        if not profile.top_agents:
            html = self._sync._fetch(_build_path(player_id, "all"))
            profile = parse_player_profile(html, timespan="all")
            profile.player_id = player_id
        return profile


def _build_path(player_id: int, timespan: str) -> str:
    return f"/player/{player_id}/?timespan={timespan}"
