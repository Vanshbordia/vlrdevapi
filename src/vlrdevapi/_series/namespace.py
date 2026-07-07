"""Top-level series namespace with curried access pattern."""

import httpx

from vlrdevapi._series.economy.namespace import SeriesEconomyNamespace
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._series.match_namespace import SeriesMatchNamespace
from vlrdevapi._series.performance.namespace import SeriesPerformanceNamespace
from vlrdevapi._series.players.namespace import SeriesPlayersNamespace
from vlrdevapi._series.rounds.namespace import SeriesRoundsNamespace
from vlrdevapi._series.vods.namespace import SeriesVodsNamespace
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesNamespace:
    """Top-level namespace for series/match data.

    Access sub-namespaces for info, vods, players, rounds, performance,
    and economy data. Use ``vlrdevapi.series(series_id)`` for curried access.

    Attributes:
        info: Sub-namespace for series info.
        vods: Sub-namespace for series VODs.
        players: Sub-namespace for player stats.
        rounds: Sub-namespace for round-by-round data.
        performance: Sub-namespace for performance metrics.
        economy: Sub-namespace for economy stats.

    Examples:
        >>> info = vlrdevapi.series.info(series_id=1)
        >>> stats = vlrdevapi.series(1).players(game_id="all")
        >>> rounds = vlrdevapi.series(1).rounds(game_id=1)
        >>> vods = vlrdevapi.series(1).vods()

    """

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._vods = SeriesVodsNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._players = SeriesPlayersNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._rounds = SeriesRoundsNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._performance = SeriesPerformanceNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._economy = SeriesEconomyNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @property
    def info(self) -> SeriesInfoNamespace:
        """Access series info sub-namespace.

        Returns:
            SeriesInfoNamespace: Sub-namespace for series info. Call with
            ``series_id`` to return a ``SeriesInfo`` model.

        Example:
            >>> info = vlrdevapi.series.info(series_id=1)

        """
        return self._info

    @property
    def vods(self) -> SeriesVodsNamespace:
        """Access VOD links sub-namespace.

        Returns:
            SeriesVodsNamespace: Sub-namespace for series VODs. Call with
            ``series_id`` to return a ``SeriesVods`` model.

        Example:
            >>> vods = vlrdevapi.series.vods(series_id=12345)

        """
        return self._vods

    @property
    def players(self) -> SeriesPlayersNamespace:
        """Access player stats sub-namespace.

        Returns:
            SeriesPlayersNamespace: Sub-namespace for player stats. Call with
            ``series_id`` and optional ``game_id`` to return a
            ``SeriesPlayers`` model.

        Example:
            >>> stats = vlrdevapi.series.players(series_id=12345, game_id="all")

        """
        return self._players

    @property
    def rounds(self) -> SeriesRoundsNamespace:
        """Access round-by-round data sub-namespace.

        Returns:
            SeriesRoundsNamespace: Sub-namespace for round data. Call with
            ``series_id`` and optional ``game_id`` to return a
            ``SeriesRounds`` model.

        Example:
            >>> rounds = vlrdevapi.series.rounds(series_id=12345, game_id=1)

        """
        return self._rounds

    @property
    def performance(self) -> SeriesPerformanceNamespace:
        """Access performance metrics sub-namespace.

        Returns:
            SeriesPerformanceNamespace: Sub-namespace for performance. Call
            with ``series_id`` to return a ``SeriesPerformance`` model.

        Example:
            >>> perf = vlrdevapi.series.performance(series_id=12345)

        """
        return self._performance

    @property
    def economy(self) -> SeriesEconomyNamespace:
        """Access economy stats sub-namespace.

        Returns:
            SeriesEconomyNamespace: Sub-namespace for economy stats. Call
            with ``series_id`` to return a ``SeriesEconomy`` model.

        Example:
            >>> eco = vlrdevapi.series.economy(series_id=12345)

        """
        return self._economy

    @sanitize_and_validate
    def __call__(self, series_id: int) -> SeriesMatchNamespace:
        """Create a curried namespace bound to a specific series.

        All subsequent calls on the returned object use ``series_id``
        automatically without needing to pass it each time.

        Args:
            series_id: The unique series identifier on vlr.gg.

        Returns:
            SeriesMatchNamespace: A namespace object with methods ``.info()``,
            ``.vods()``, ``.players()``, ``.rounds()``, ``.performance()``,
            and ``.economy()`` — all pre-bound to the given ``series_id``.

        Raises:
            ValidationError: If ``series_id`` is not a valid positive integer.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> ns.info().team1.name
            'FNATIC'
            >>> ns.players(game_id="all").team1.players[0].name
            'Boaster'

        """
        return SeriesMatchNamespace(
            series_id=series_id,
            info=self._info,
            vods=self._vods,
            players=self._players,
            rounds=self._rounds,
            performance=self._performance,
            economy=self._economy,
        )



