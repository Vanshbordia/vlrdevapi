"""Player info namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.info.models import PlayerInfo
from vlrdevapi._player.info.parser import parse_player_info
from vlrdevapi._utils.paths import player as player_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class PlayerInfoNamespace:
    """Access player information from vlr.gg."""

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
    def __call__(self, player_id: int) -> PlayerInfo:
        """Get detailed information about a player.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerInfo: Player details including ``name``, ``real_name``,
            ``country``, ``country_code``, ``player_id``, and social media
            links (``twitter``, ``twitch``, ``youtube``).

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.info(player_id=11225)
            >>> result.name
            'zekken'
            >>> result.country
            'United States'

        """
        html = self._sync._fetch(player_path(player_id))
        result = parse_player_info(html)
        result.player_id = player_id
        return result
