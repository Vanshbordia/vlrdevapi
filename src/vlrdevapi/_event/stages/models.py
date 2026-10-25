
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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

class EventStages(ExportableModel):
    """Collection of stages for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of stages for an event."},
    )

    stages: list[EventStage] = Field(
        default_factory=list, description="List of stages in the event",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert event stages to tabular records."""
        records: list[dict[str, Any]] = []
        for s in self.stages:
            stage_id = s.id or None
            records.append({
                "stage_id": stage_id,
                "stage_name": s.name or "All",
                "start_date": s.start_date.isoformat() if s.start_date else None,
                "end_date": s.end_date.isoformat() if s.end_date else None,
            })
        return records

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]
