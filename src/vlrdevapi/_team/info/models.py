from pydantic import BaseModel, ConfigDict, Field


class TeamSocial(BaseModel):
    """Team social media information."""

    name: str = Field(description="Platform name (e.g., 'Twitch', 'YouTube')")
    url: str = Field(description="Full URL to the social media profile")


class TeamSuccessor(BaseModel):
    """Team successor information."""

    id: int = Field(description="Team ID")
    name: str = Field(description="Team name")


class TeamInfo(BaseModel):
    """Team information from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team information from vlr.gg."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name")
    tag: str = Field(default="", description="Short team tag")
    light_logo_url: str = Field(
        default="", description="URL to the team light logo image",
    )
    dark_logo_url: str = Field(
        default="", description="URL to the team dark logo image",
    )
    country: str = Field(default="", description="Team country name")
    is_active: bool = Field(default=True, description="Whether the team is active")
    socials: list[TeamSocial] | None = Field(
        default=None, description="List of team social media profiles",
    )
    previous_teams: list[TeamSuccessor] | None = Field(
        default=None, description="List of previous team names/IDs",
    )
    current_teams: list[TeamSuccessor] | None = Field(
        default=None, description="List of current team names/IDs",
    )
