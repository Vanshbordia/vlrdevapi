"""Team placements namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._team.placements.models import TeamPlacements
from vlrdevapi._team.placements.parser import parse_team_placements
from vlrdevapi._utils.paths import team as team_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class TeamPlacementsNamespace:
    """Access team placements from vlr.gg."""

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
    def __call__(self, team_id: int) -> TeamPlacements:
        """Get event placements for a team.

        Args:
            team_id: The unique team identifier on vlr.gg.

        Returns:
            TeamPlacements: Placement history including ``event_name``, ``stage``, ``placement``/``rank``, ``prize``, and ``total_winnings``.

        Raises:
            ValidationError: If ``team_id`` is not a valid positive integer.
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.team.placements(team_id=4568)
            >>> result.placements[0].placement
            1

        """
        html = self._sync._fetch(team_path(team_id))
        return parse_team_placements(html, team_id)

