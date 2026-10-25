from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class TeamStanding(BaseModel):
    """Team information in standings from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team information in standings from vlr.gg."},
    )

    id: int | None = Field(
        default=None,
        description="Team ID from vlr.gg, None for TBD",
    )
    name: str = Field(
        default="",
        description="Team name (e.g., 'FURIA', 'TBD')",
    )
    country: str | None = Field(
        default=None,
        description="Team country (e.g., 'Brazil')",
    )
    logo_url: str | None = Field(
        default=None,
        description="Team logo URL",
    )


class StandingEntry(BaseModel):
    """A single standing entry from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single standing entry from vlr.gg."},
    )

    place: str = Field(
        default="",
        description="Place (e.g., '1st', '2nd', '3rd-4th')",
    )
    prize_money: int | None = Field(
        default=None,
        description="Prize money as numeric value (e.g., 125000), None if none",
    )
    prize_currency: str | None = Field(
        default=None,
        description="Prize currency symbol (e.g., '$', '€'), None if none",
    )
    team: TeamStanding = Field(
        default_factory=TeamStanding,
        description="Team information",
    )
    points: int | None = Field(
        default=None,
        description="Circuit points (e.g., 4), None if not present",
    )
    note: str | None = Field(
        default=None,
        description="Additional note (e.g., 'Masters Santiago'), None if not present",
    )


class EventStageStandings(BaseModel):
    """Standings for an event stage from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Standings for an event stage from vlr.gg."},
    )

    stage_path: str = Field(
        default="",
        description="Stage path (e.g., 'group-stage')",
    )
    stage_name: str = Field(
        default="",
        description="Stage name (e.g., 'Group Stage')",
    )
    standings: list[StandingEntry] = Field(
        default_factory=list,
        description="List of standing entries for this stage",
    )

class EventStandings(ExportableModel):
    """Wrapper for standings grouped by stage."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Wrapper for event standings."},
    )
    stages: list[EventStageStandings] = Field(
        default_factory=list,
        description="List of stages containing standings",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten event standings into tabular records (1 row per team placement)."""
        records: list[dict[str, Any]] = []
        for stage in self.stages:
            for s in stage.standings:
                t_name = (s.team.name if s.team else "") or "TBD"
                t_id = s.team.id if (s.team and s.team.id) else None
                records.append({
                    "stage_name": stage.stage_name,
                    "stage_path": stage.stage_path,
                    "place": s.place,
                    "team_id": t_id,
                    "team_name": t_name,
                    "team_country": s.team.country if s.team else "",
                    "prize_money": s.prize_money,
                    "prize_currency": s.prize_currency or "",
                    "points": s.points,
                    "note": s.note or "",
                    "url": f"https://www.vlr.gg/team/{t_id}" if t_id else "",
                })
        return records

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]
