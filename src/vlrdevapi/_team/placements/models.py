
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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


class TeamPlacements(ExportableModel):
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

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten tournament placements into tabular records (1 row per placement stage)."""
        records: list[dict[str, Any]] = []
        for ep in self.placements:
            if ep.placements:
                for p in ep.placements:
                    records.append({
                        "team_id": self.team_id,
                        "event_id": ep.event_id,
                        "event_name": ep.event_name,
                        "year": ep.year,
                        "stage": p.stage or None,
                        "placement": p.placement,
                        "prize": ep.prize,
                        "prize_currency": ep.prize_currency,
                        "url": f"https://www.vlr.gg/event/{ep.event_id}" if ep.event_id else None,
                    })
            else:
                records.append({
                    "team_id": self.team_id,
                    "event_id": ep.event_id,
                    "event_name": ep.event_name,
                    "year": ep.year,
                    "stage": None,
                    "placement": None,
                    "prize": ep.prize,
                    "prize_currency": ep.prize_currency,
                    "url": f"https://www.vlr.gg/event/{ep.event_id}" if ep.event_id else None,
                })
        return records
