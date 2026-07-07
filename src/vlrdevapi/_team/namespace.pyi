from datetime import date

from vlrdevapi._team.completed_matches.namespace import TeamCompletedMatchesNamespace
from vlrdevapi._team.completed_matches.models import TeamCompletedMatches
from vlrdevapi._team.info.models import TeamInfo
from vlrdevapi._team.info.namespace import TeamInfoNamespace
from vlrdevapi._team.placements.models import TeamPlacements
from vlrdevapi._team.placements.namespace import TeamPlacementsNamespace
from vlrdevapi._team.roster.models import TeamRoster
from vlrdevapi._team.roster.namespace import TeamRosterNamespace
from vlrdevapi._team.stats.models import AgentCompositionLevel, TeamStats
from vlrdevapi._team.stats.namespace import TeamStatsNamespace
from vlrdevapi._team.transactions.models import TeamTransactions
from vlrdevapi._team.transactions.namespace import TeamTransactionsNamespace
from vlrdevapi._team.upcoming_matches.models import TeamUpcomingMatches
from vlrdevapi._team.upcoming_matches.namespace import TeamUpcomingMatchesNamespace
from vlrdevapi.fetcher import RateLimiter, RetryConfig
import httpx


class TeamMatchNamespace:
    def __init__(
        self,
        team_id: int,
        info: TeamInfoNamespace,
        roster: TeamRosterNamespace,
        completed_matches: TeamCompletedMatchesNamespace,
        upcoming_matches: TeamUpcomingMatchesNamespace,
        transactions: TeamTransactionsNamespace,
        stats: TeamStatsNamespace,
        placements: TeamPlacementsNamespace,
    ) -> None: ...

    def info(self) -> TeamInfo: ...

    def roster(self) -> TeamRoster: ...

    def completed_matches(self) -> TeamCompletedMatches: ...

    def upcoming_matches(self) -> TeamUpcomingMatches: ...

    def transactions(self) -> TeamTransactions: ...

    def stats(
        self,
        date_start: date | None = None,
        date_end: date | None = None,
        event_id: int | None = None,
        series_id: int | None = None,
        subseries_id: int | None = None,
        last_days: int | None = None,
        agent_composition: AgentCompositionLevel = "none",
    ) -> TeamStats: ...

    def placements(self) -> TeamPlacements: ...


class TeamNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def info(self) -> TeamInfoNamespace: ...

    @property
    def roster(self) -> TeamRosterNamespace: ...

    @property
    def completed_matches(self) -> TeamCompletedMatchesNamespace: ...

    @property
    def upcoming_matches(self) -> TeamUpcomingMatchesNamespace: ...

    @property
    def transactions(self) -> TeamTransactionsNamespace: ...

    @property
    def stats(self) -> TeamStatsNamespace: ...

    @property
    def placements(self) -> TeamPlacementsNamespace: ...

    def __call__(self, team_id: int) -> TeamMatchNamespace: ...
