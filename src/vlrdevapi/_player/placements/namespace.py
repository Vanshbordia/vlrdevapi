"""Player placements namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.placements.models import PlayerPlacements
from vlrdevapi._player.placements.parser import parse_player_placements
from vlrdevapi._utils.paths import player as player_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class PlayerPlacementsNamespace:
    """Access event placements for a player from vlr.gg."""

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
    def __call__(self, player_id: int) -> PlayerPlacements:
        """Get event placements and total winnings for a player.

        Args:
            player_id: The unique player identifier on vlr.gg.

        Returns:
            PlayerPlacements: Placement history including event, stage,
            placement, prize, and total winnings.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.placements(player_id=46051)
            >>> result.total_winnings
            5082
            >>> result.placements[0].placement
            '2nd'

        """
        html = self._sync._fetch(player_path(player_id))
        return parse_player_placements(html, player_id)
