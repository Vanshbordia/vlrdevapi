"""Curried namespace for individual series access."""

from vlrdevapi._series.economy.models import EconomyData
from vlrdevapi._series.economy.namespace import SeriesEconomyNamespace
from vlrdevapi._series.info.models import SeriesInfo
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._series.performance.models import PerformanceData
from vlrdevapi._series.performance.namespace import SeriesPerformanceNamespace
from vlrdevapi._series.players.models import PlayersStats
from vlrdevapi._series.players.namespace import SeriesPlayersNamespace
from vlrdevapi._series.rounds.models import RoundsData
from vlrdevapi._series.rounds.namespace import SeriesRoundsNamespace
from vlrdevapi._series.vods.models import SeriesVods
from vlrdevapi._series.vods.namespace import SeriesVodsNamespace
from vlrdevapi.validators import sanitize_and_validate


class SeriesMatchNamespace:
    """Curried namespace bound to a specific series_id (sync).

    Provides access to all series sub-namespaces with the series_id pre-bound.
    Each method call is an independent fetch (no caching).
    """

    def __init__(
        self,
        series_id: int,
        info: SeriesInfoNamespace,
        vods: SeriesVodsNamespace,
        players: SeriesPlayersNamespace,
        rounds: SeriesRoundsNamespace,
        performance: SeriesPerformanceNamespace,
        economy: SeriesEconomyNamespace,
    ):
        self._series_id = series_id
        self._info = info
        self._vods = vods
        self._players = players
        self._rounds = rounds
        self._performance = performance
        self._economy = economy

    @sanitize_and_validate
    def info(self) -> SeriesInfo:
        """Get overview info for this series.

        Returns:
            SeriesInfo: Series metadata including ``team1``, ``team2``,
            ``event_name``, ``scores``, ``match_format`` (bo3/bo5),
            ``status``, and ``patch``.

        Raises:
            ValidationError: If the bound ``series_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> ns.info().team1.name
            'FNATIC'
            >>> ns.info().event_name
            'VCT LOCK//IN São Paulo'

        """
        return self._info(self._series_id)

    @sanitize_and_validate
    def vods(self) -> SeriesVods:
        """Get VOD/video links for this series.

        Returns:
            SeriesVods: VOD metadata including ``games`` (list of
            ``GameVods`` with ``youtube`` and ``twitch`` URLs
            per game), and ``event_name``.

        Raises:
            ValidationError: If the bound ``series_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> ns.vods().games[0].youtube
            'https://www.youtube.com/watch?v=...'

        """
        return self._vods(self._series_id)

    @sanitize_and_validate
    def players(self, game_id: int | str = "all") -> PlayersStats:
        """Get per-game player statistics for this series.

        Args:
            game_id: Game number within the series, or "all" for aggregate stats.

        Returns:
            PlayersStats: Player statistics for both teams including
            ``team1`` and ``team2`` (``TeamPlayers`` with per-player stats
            comprising ACS, K/D, ADR, KAST, and first-kill data).

        Raises:
            ValidationError: If the bound ``series_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> ns.players(game_id="all").team1.players[0].name
            'Boaster'

        """
        return self._players(self._series_id, game_id)

    @sanitize_and_validate
    def rounds(self, game_id: int) -> RoundsData:
        """Get round-by-round data for a game in this series.

        Args:
            game_id: Game number within the series (1-based).

        Returns:
            RoundsData: Round-by-round data including ``rounds``
            (list of ``RoundDetail`` with economy, damage, and kill
            events), ``team_defense``, ``team_attack``, and enriched
            team IDs.

        Raises:
            ValidationError: If the bound ``series_id`` or ``game_id``
                is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> data = ns.rounds(game_id=1)
            >>> len(data.rounds)
            24

        """
        return self._rounds(self._series_id, game_id)

    @sanitize_and_validate
    def performance(self, game_id: int | str = "all") -> PerformanceData:
        """Get performance metrics for a game in this series.

        Args:
            game_id: Game number within the series, or "all" for aggregate.

        Returns:
            PerformanceData: Performance metrics including
            ``all_kills_matrix``, ``first_kills_matrix``,
            ``op_kills_matrix`` (each a ``KillMatrix`` of ``KillEntry``
            items), and ``adv_stats`` (list of ``AdvStatsEntry`` with
            multi-kill, clutch, plant/defuse, and econ data).

        Raises:
            ValidationError: If the bound ``series_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> perf = ns.performance(game_id="all")
            >>> perf.adv_stats[0].three_k
            2

        """
        return self._performance(self._series_id, game_id)

    @sanitize_and_validate
    def economy(self, game_id: int) -> EconomyData:
        """Get economy data for a game in this series.

        Args:
            game_id: Game number within the series (1-based).

        Returns:
            EconomyData: Economy data including ``rounds`` (list of
            ``EconomyRound`` with purchases, remaining credits, and
            team spending per round), ``team1`` and ``team2`` names,
            and enriched team IDs.

        Raises:
            ValidationError: If the bound ``series_id`` or ``game_id``
                is not a valid positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> ns = vlrdevapi.series(12345)
            >>> econ = ns.economy(game_id=1)
            >>> econ.rounds[0].team1_creds
            24000

        """
        return self._economy(self._series_id, game_id)



