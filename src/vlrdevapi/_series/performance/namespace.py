"""Series performance namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.performance.models import PerformanceData
from vlrdevapi._series.performance.parser import parse_performance_data
from vlrdevapi._series.players.parser import parse_players_stats
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


def _get_player_mapping_sync(ns: SyncNamespace, series_id: int) -> dict[str, int]:
    """Fetch player name-to-ID mapping from the series page.

    Args:
        ns: SyncNamespace instance for HTTP requests.
        series_id: The unique series identifier on vlr.gg.

    Returns:
        dict[str, int]: Mapping of player names to player IDs.

    """
    html = ns._fetch(f"{series_path(series_id)}/?game=all&tab=overview")
    players_stats = parse_players_stats(html, game_id="all")
    mapping: dict[str, int] = {}
    for team in [players_stats.team1, players_stats.team2]:
        for player in team.players:
            mapping[player.name] = player.player_id
    return mapping


class SeriesPerformanceNamespace:
    """Access performance metrics for a series game from vlr.gg."""

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
    def __call__(self, series_id: int, game_id: int | str = "all") -> PerformanceData:
        """Get performance metrics for a series game on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The unique game/map identifier ("all" for combined, or numeric ID).

        Returns:
            PerformanceData: Performance metrics including ``all_kills_matrix``,
            ``first_kills_matrix``, ``op_kills_matrix`` (each a ``KillMatrix``
            of ``KillEntry`` items), and ``adv_stats`` (list of ``AdvStatsEntry``
            with multi-kill, clutch, plant/defuse, and econ data).

        Raises:
            ValidationError: If ``series_id`` is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> perf = vlrdevapi.series.performance(series_id=12345, game_id="all")
            >>> perf.all_kills_matrix.killers()[:3]
            ['Boaster', 'Derke', 'Chronicle']
            >>> perf.adv_stats[0].three_k
            2

        """
        gid = str(game_id)
        player_mapping = _get_player_mapping_sync(self._sync, series_id)
        html = self._sync._fetch(f"{series_path(series_id)}/?game={gid}&tab=performance")
        result = parse_performance_data(html, game_id=gid, player_mapping=player_mapping)
        result.series_id = series_id
        result.game_id = gid
        return result


