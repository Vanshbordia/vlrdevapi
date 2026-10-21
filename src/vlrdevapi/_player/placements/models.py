from pydantic import BaseModel, ConfigDict, Field


class PlayerEventPlacement(BaseModel):
    """A single event placement for a player."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single event placement for a player."},
    )

    event_id: int = Field(default=0, description="Event ID on vlr.gg")
    event_name: str = Field(default="", description="Event name")
    year: int = Field(default=0, description="Year of the event")
    stage: str = Field(
        default="", description="Stage within the event (e.g. 'Playoffs')",
    )
    placement: str = Field(
        default="", description="Placement (e.g. '1st', '5th-8th')",
    )
    prize_amount: int | None = Field(
        default=None, description="Prize money for this placement, None if none",
    )
    prize_currency: str | None = Field(
        default=None, description="Currency symbol (e.g. '$'), None if no prize",
    )
    team_name: str = Field(default="", description="Team the player represented")


class PlayerPlacements(BaseModel):
    """Event placements and total winnings for a player."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Event placements and total winnings for a player.",
        },
    )

    player_id: int = Field(default=0, description="Player ID on vlr.gg")
    total_winnings: int | None = Field(
        default=None, description="Total prize money as a numeric value",
    )
    total_winnings_currency: str | None = Field(
        default=None, description="Currency symbol for total winnings (e.g. '$')",
    )
    placements: list[PlayerEventPlacement] = Field(
        default_factory=list,
        description="List of individual event placements",
    )
