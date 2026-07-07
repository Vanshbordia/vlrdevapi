from pydantic import BaseModel, ConfigDict, Field


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

class EventStandings(BaseModel):
    """Wrapper for standings grouped by stage."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Wrapper for event standings."},
    )
    stages: list[EventStageStandings] = Field(
        default_factory=list,
        description="List of stages containing standings",
    )

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]
