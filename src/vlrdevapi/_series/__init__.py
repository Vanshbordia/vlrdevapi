"""Series/match-level data: info, vods, players, rounds, performance, economy."""

from vlrdevapi._series.economy.namespace import SeriesEconomyNamespace
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._series.match_namespace import SeriesMatchNamespace
from vlrdevapi._series.namespace import SeriesNamespace
from vlrdevapi._series.performance.namespace import SeriesPerformanceNamespace
from vlrdevapi._series.players.namespace import SeriesPlayersNamespace
from vlrdevapi._series.rounds.namespace import SeriesRoundsNamespace
from vlrdevapi._series.vods.namespace import SeriesVodsNamespace

__all__ = [
    "SeriesEconomyNamespace",
    "SeriesInfoNamespace",
    "SeriesMatchNamespace",
    "SeriesNamespace",
    "SeriesPerformanceNamespace",
    "SeriesPlayersNamespace",
    "SeriesRoundsNamespace",
    "SeriesVodsNamespace",
]
