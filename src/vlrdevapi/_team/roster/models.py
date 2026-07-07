
from pydantic import BaseModel, ConfigDict, Field


class Player(BaseModel):
    """Player or staff member information."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Player or staff member information."},
    )

    id: int = Field(description="Unique player identifier on vlr.gg")
    ign: str = Field(default="", description="In-game name")
    real_name: str = Field(default="", description="Real name")
    country: str = Field(default="", description="Country name")
    roles: list[str] = Field(
        default_factory=list,
        description="List of roles (e.g., ['Player'], ['Head Coach'])",
    )
    is_captain: bool = Field(
        default=False, description="Whether the player is team captain",
    )
    photo_url: str = Field(default="", description="Photo URL")
    is_active: bool = Field(default=True, description="Whether the player is active")
    is_sub: bool = Field(
        default=False, description="Whether the player is a substitute",
    )


class TeamRoster(BaseModel):
    """Team roster information from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team roster information from vlr.gg."},
    )

    players: list[Player] = Field(default_factory=list, description="List of players")
    staff: list[Player] = Field(
        default_factory=list, description="List of staff members",
    )
