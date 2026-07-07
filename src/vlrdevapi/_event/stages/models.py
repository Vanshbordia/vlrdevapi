
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EventStage(BaseModel):
    """Stage information for an event from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Stage information for an event from vlr.gg."},
    )

    name: str = Field(
        default="",
        description="Stage name (e.g., 'All', 'Playoffs', 'Group Stage')",
    )
    id: str = Field(
        default="",
        description="Stage identifier from series_id parameter (e.g., 'all', '5556', '5557')",
    )
    start_date: date | None = Field(
        default=None,
        description="Stage start date inferred from the event page subnav date range",
    )
    end_date: date | None = Field(
        default=None,
        description="Stage end date inferred from the event page subnav date range",
    )

class EventStages(BaseModel):
    """Collection of stages for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of stages for an event."},
    )

    stages: list[EventStage] = Field(
        default_factory=list, description="List of stages in the event",
    )

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]
