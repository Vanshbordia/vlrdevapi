"""Series players namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.players.models import PlayersStats
from vlrdevapi._series.players.parser import parse_players_stats
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesPlayersNamespace:
    """Access per-game player statistics from vlr.gg."""

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
    def __call__(self, series_id: int, game_id: int | str = "all") -> PlayersStats:
        """Get per-game player statistics for a series match on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The game/map identifier ("all" for combined, or numeric ID).

        Returns:
            PlayersStats: Player statistics for both teams including
            ``team1`` and ``team2`` (``TeamPlayers`` with per-player stats
            comprising ACS, K/D, ADR, KAST, and first-kill data).

        Raises:
            ValidationError: If ``series_id`` is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> stats = vlrdevapi.series.players(series_id=12345, game_id="all")
            >>> stats.team1.players[0].name
            'Boaster'
            >>> stats.team1.players[0].stats.overall.acs
            245.3

        """
        gid = str(game_id)
        html = self._sync._fetch(f"{series_path(series_id)}/?game={gid}&tab=overview")
        result = parse_players_stats(html, game_id=gid)
        result.series_id = series_id
        result.game_id = gid
        return result

