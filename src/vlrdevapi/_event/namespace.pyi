from typing import Literal

from vlrdevapi._event.info.models import EventInfo
from vlrdevapi._event.info.namespace import EventInfoNamespace
from vlrdevapi._event.list.namespace import EventListNamespace
from vlrdevapi._event.matches.models import EventMatches
from vlrdevapi._event.matches.namespace import EventMatchesNamespace
from vlrdevapi._event.stages.models import EventStages
from vlrdevapi._event.stages.namespace import EventStagesNamespace
from vlrdevapi._event.standings.models import EventStandings
from vlrdevapi._event.standings.namespace import EventStandingsNamespace
from vlrdevapi._event.teams.models import EventTeams
from vlrdevapi._event.teams.namespace import EventTeamsNamespace
from vlrdevapi.fetcher import RateLimiter, RetryConfig
import httpx


class EventMatchNamespace:
    def __init__(
        self,
        event_id: int,
        info: EventInfoNamespace,
        stages: EventStagesNamespace,
        teams: EventTeamsNamespace,
        matches: EventMatchesNamespace,
        standings: EventStandingsNamespace,
    ) -> None: ...

    def info(self) -> EventInfo: ...

    def stages(self) -> EventStages: ...

    def teams(self, stage: str | None = None) -> EventTeams: ...

    def matches(
        self,
        stage_id: str | None = None,
        state: Literal["all", "completed", "live", "upcoming"] = "all",
    ) -> EventMatches: ...

    def standings(self, stage: str | None = None) -> EventStandings: ...


class EventNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def info(self) -> EventInfoNamespace: ...

    @property
    def stages(self) -> EventStagesNamespace: ...

    @property
    def teams(self) -> EventTeamsNamespace: ...

    @property
    def matches(self) -> EventMatchesNamespace: ...

    @property
    def standings(self) -> EventStandingsNamespace: ...

    @property
    def list(self) -> EventListNamespace: ...

    def __call__(self, event_id: int) -> EventMatchNamespace: ...
