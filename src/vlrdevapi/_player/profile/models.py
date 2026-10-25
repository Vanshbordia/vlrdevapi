
from typing import Any

from pydantic import ConfigDict, Field

from vlrdevapi._player.agents.models import AgentStats
from vlrdevapi._player.teams.models import PlayerTeam
from vlrdevapi.commons.export import ExportableModel


class PlayerProfile(ExportableModel):
    """Consolidated player profile summary from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Consolidated player profile summary from vlr.gg.",
        },
    )

    player_id: int = Field(default=0, description="Unique player identifier on vlr.gg")
    name: str = Field(default="", description="Player in-game name")
    real_name: str = Field(default="", description="Player's real name")
    img: str = Field(default="", description="URL to the player's profile image")
    x_link: str = Field(default="", description="Player's X (Twitter) profile URL")
    x_handle: str = Field(default="", description="Player's X (Twitter) handle")
    twitch_link: str = Field(default="", description="Player's Twitch profile URL")
    twitch_handle: str = Field(default="", description="Player's Twitch handle")
    country: str = Field(
        default="", description="Player's country of origin (e.g. 'UNITED STATES')",
    )
    country_code: str = Field(
        default="", description="Two-letter country code (e.g. 'us')",
    )
    aliases: list[str] = Field(
        default=[], description="Player's known aliases / former names",
    )
    current_team: PlayerTeam | None = Field(
        default=None, description="Player's current team, if any",
    )
    top_agents: list[AgentStats] = Field(
        default_factory=list,
        description="Most played agents, sorted by usage (most played first)",
    )
    stats_timespan: str = Field(
        default="",
        description="Timespan used for agent stats ('30d' or 'all')",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert player profile to tabular records."""
        primary_agent = self.top_agents[0].agent if self.top_agents else None
        primary_agent_use = self.top_agents[0].use if self.top_agents else None
        return [{
            "player_id": self.player_id,
            "name": self.name,
            "real_name": self.real_name or None,
            "country": self.country or None,
            "country_code": self.country_code or None,
            "current_team_id": self.current_team.team_id if self.current_team else None,
            "current_team_name": (self.current_team.name if self.current_team else "") or "TBD",
            "x_handle": self.x_handle or None,
            "twitch_handle": self.twitch_handle or None,
            "aliases": list(self.aliases) if self.aliases else [],
            "primary_agent": primary_agent,
            "primary_agent_use": primary_agent_use,
            "top_agents": [a.agent for a in self.top_agents] if self.top_agents else [],
            "stats_timespan": self.stats_timespan or None,
            "url": f"https://www.vlr.gg/player/{self.player_id}",
        }]
