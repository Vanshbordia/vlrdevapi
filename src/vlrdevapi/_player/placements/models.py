from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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


class PlayerPlacements(ExportableModel):
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

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert player placements to tabular records."""
        records: list[dict[str, Any]] = []
        for p in self.placements:
            records.append({
                "player_id": self.player_id,
                "event_id": p.event_id,
                "event_name": p.event_name,
                "year": p.year,
                "stage": p.stage,
                "placement": p.placement,
                "prize_amount": p.prize_amount,
                "prize_currency": p.prize_currency,
                "team_name": p.team_name or "TBD",
                "url": f"https://www.vlr.gg/event/{p.event_id}" if p.event_id else "",
            })
        return records
