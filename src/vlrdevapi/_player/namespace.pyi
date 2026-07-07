from typing import Literal

from vlrdevapi._player.agents.models import AgentStatsPage
from vlrdevapi._player.agents.namespace import AgentsNamespace
from vlrdevapi._player.info.models import PlayerInfo
from vlrdevapi._player.info.namespace import PlayerInfoNamespace
from vlrdevapi._player.matches.models import PlayerMatches
from vlrdevapi._player.matches.namespace import MatchesNamespace
from vlrdevapi._player.profile.models import PlayerProfile
from vlrdevapi._player.profile.namespace import ProfileNamespace
from vlrdevapi._player.teams.models import PlayerTeams
from vlrdevapi._player.teams.namespace import PlayerTeamsNamespace
from vlrdevapi.fetcher import RateLimiter, RetryConfig
import httpx


class PlayerMatchNamespace:
    def __init__(
        self,
        player_id: int,
        info: PlayerInfoNamespace,
        teams: PlayerTeamsNamespace,
        agents: AgentsNamespace,
        matches: MatchesNamespace,
        profile: ProfileNamespace,
    ) -> None: ...

    def info(self) -> PlayerInfo: ...

    def teams(self) -> PlayerTeams: ...

    def agents(self, timespan: Literal["30d", "60d", "90d", "all"] = "all") -> AgentStatsPage: ...

    def matches(self, limit: int = 20) -> PlayerMatches: ...

    def profile(self) -> PlayerProfile: ...


class PlayerNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def info(self) -> PlayerInfoNamespace: ...

    @property
    def teams(self) -> PlayerTeamsNamespace: ...

    @property
    def agents(self) -> AgentsNamespace: ...

    @property
    def matches(self) -> MatchesNamespace: ...

    @property
    def profile(self) -> ProfileNamespace: ...

    def __call__(self, player_id: int) -> PlayerMatchNamespace: ...
