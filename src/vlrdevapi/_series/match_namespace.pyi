from datetime import tzinfo
from zoneinfo import ZoneInfo

from vlrdevapi._series.economy.models import EconomyData
from vlrdevapi._series.economy.namespace import SeriesEconomyNamespace
from vlrdevapi._series.info.models import SeriesInfo
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._series.performance.models import PerformanceData
from vlrdevapi._series.performance.namespace import SeriesPerformanceNamespace
from vlrdevapi._series.players.models import PlayersStats
from vlrdevapi._series.players.namespace import SeriesPlayersNamespace
from vlrdevapi._series.replay.models import ReplayData
from vlrdevapi._series.replay.namespace import SeriesReplayNamespace
from vlrdevapi._series.rounds.models import RoundsData
from vlrdevapi._series.rounds.namespace import SeriesRoundsNamespace
from vlrdevapi._series.vods.models import SeriesVods
from vlrdevapi._series.vods.namespace import SeriesVodsNamespace

class SeriesMatchNamespace:
    def __init__(
        self,
        series_id: int,
        info: SeriesInfoNamespace,
        vods: SeriesVodsNamespace,
        players: SeriesPlayersNamespace,
        rounds: SeriesRoundsNamespace,
        performance: SeriesPerformanceNamespace,
        economy: SeriesEconomyNamespace,
        replay: SeriesReplayNamespace,
        source_tz: ZoneInfo | tzinfo | None = None,
    ) -> None: ...

    def info(self) -> SeriesInfo:
        ...

    def vods(self) -> SeriesVods:
        ...

    def players(self, game_id: int | str = "all") -> PlayersStats:
        ...

    def rounds(self, game_id: int) -> RoundsData:
        ...

    def performance(self, game_id: int | str = "all") -> PerformanceData:
        ...

    def economy(self, game_id: int) -> EconomyData:
        ...

    def replay(self, game_id: int) -> ReplayData:
        ...
