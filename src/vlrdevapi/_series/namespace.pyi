from vlrdevapi._series.economy.namespace import SeriesEconomyNamespace
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._series.match_namespace import SeriesMatchNamespace
from vlrdevapi._series.performance.namespace import SeriesPerformanceNamespace
from vlrdevapi._series.players.namespace import SeriesPlayersNamespace
from vlrdevapi._series.rounds.namespace import SeriesRoundsNamespace
from vlrdevapi._series.vods.namespace import SeriesVodsNamespace
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class SeriesNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def info(self) -> SeriesInfoNamespace: ...

    @property
    def vods(self) -> SeriesVodsNamespace: ...

    @property
    def players(self) -> SeriesPlayersNamespace: ...

    @property
    def rounds(self) -> SeriesRoundsNamespace: ...

    @property
    def performance(self) -> SeriesPerformanceNamespace: ...

    @property
    def economy(self) -> SeriesEconomyNamespace: ...

    def __call__(self, series_id: int) -> SeriesMatchNamespace: ...
