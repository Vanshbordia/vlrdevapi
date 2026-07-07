
from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi._player.agents.models import AgentStats
from vlrdevapi._player.teams.models import PlayerTeam


class PlayerProfile(BaseModel):
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
