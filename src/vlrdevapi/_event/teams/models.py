from pydantic import BaseModel, ConfigDict, Field


class Team(BaseModel):
    """Team information for an event from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team information for an event from vlr.gg."},
    )

    name: str = Field(
        default="",
        description="Team name (e.g., 'NRG')",
    )
    id: int = Field(
        default=0,
        description="Team identifier from vlr.gg (e.g., 1034)",
    )
    note: str | None = Field(
        default=None,
        description="Optional note (e.g., 'Partner Team')",
    )


class EventStageTeams(BaseModel):
    """Teams grouped by event stage from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Teams grouped by event stage from vlr.gg."},
    )

    stage_path: str = Field(
        default="",
        description="Stage path (e.g., 'group-stage')",
    )
    stage_name: str = Field(
        default="",
        description="Stage name (e.g., 'Group Stage')",
    )
    teams: list[Team] = Field(
        default_factory=list,
        description="List of teams in this stage",
    )

class EventTeams(BaseModel):
    """Wrapper for teams grouped by stage."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Wrapper for event teams."},
    )
    stages: list[EventStageTeams] = Field(
        default_factory=list,
        description="List of stages containing teams",
    )

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]
