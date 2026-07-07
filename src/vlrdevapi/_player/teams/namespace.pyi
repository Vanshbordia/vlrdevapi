from vlrdevapi._player.teams.models import PlayerPastTeams, PlayerTeam, PlayerTeams
import httpx
from vlrdevapi.fetcher import RateLimiter, RetryConfig

class PlayerTeamsNamespace:
    def __init__(
        self,
        client: httpx.Client,
        timeout: int = ...,
        retry_config: RetryConfig = ...,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None: ...

    def current_team(self, player_id: int) -> PlayerTeam | None:
        ...

    def past_teams(self, player_id: int) -> PlayerPastTeams:
        ...

    def __call__(self, player_id: int) -> PlayerTeams:
        ...
