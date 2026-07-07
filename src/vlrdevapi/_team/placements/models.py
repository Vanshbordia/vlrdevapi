
from pydantic import BaseModel, ConfigDict, Field


class EventPlacement(BaseModel):
    """A single placement within an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single placement within an event."},
    )

    stage: str = Field(
        default="", description="Stage within event (e.g., 'Playoffs', 'Group Stage')",
    )
    placement: str = Field(
        default="", description="Placement (e.g., '1st', '2nd', '3rd', '5th-8th')",
    )


class TeamEventPlacement(BaseModel):
    """Event placement entry for a team."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Event placement entry for a team."},
    )

    event_id: int = Field(default=0, description="Event ID on vlr.gg")
    event_name: str = Field(default="", description="Event name")
    year: int = Field(default=0, description="Year of the event")
    placements: list[EventPlacement] = Field(
        default_factory=list,
        description="List of placements (can have multiple, e.g., Group Stage + Playoffs)",
    )
    prize: int | None = Field(
        default=None, description="Prize money as numeric value, None if no prize",
    )
    prize_currency: str | None = Field(
        default=None, description="Currency symbol (e.g., '$', '€'), None if no prize",
    )


class TeamPlacements(BaseModel):
    """Collection of team event placements."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of team event placements."},
    )

    team_id: int = Field(default=0, description="Team ID")
    total_winnings: int | None = Field(
        default=None, description="Total prize money as numeric value, None if none",
    )
    total_winnings_currency: str | None = Field(
        default=None, description="Currency symbol, None if no winnings",
    )
    placements: list[TeamEventPlacement] = Field(
        default_factory=list,
        description="List of event placements",
    )
