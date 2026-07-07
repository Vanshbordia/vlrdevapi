
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vlrdevapi._event.info.models import EventPrize


class EventListItem(BaseModel):
    """A single event from the events listing page."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single event from the events listing page.",
        },
    )

    id: int = Field(default=0, description="Unique event identifier on vlr.gg")
    name: str = Field(default="", description="Event title")
    status: Literal["ongoing", "upcoming", "completed", "paused"] = Field(
        default="upcoming", description="Event status",
    )
    prize: EventPrize | None = Field(default=None, description="Prize information")
    start_date: date | None = Field(default=None, description="Event start date")
    end_date: date | None = Field(default=None, description="Event end date")
    region: str = Field(default="", description="Country or region name from flag")
    image_url: str = Field(default="", description="URL to the event thumbnail image")
    url: str = Field(default="", description="Full URL to the event page on vlr.gg")


class EventListPagination(BaseModel):
    """Pagination metadata for event listings."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Pagination metadata for event listings."},
    )

    current_page: int = Field(default=1, description="Current page number")
    total_pages: int = Field(default=1, description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Whether a next page exists."""
        return self.current_page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Whether a previous page exists."""
        return self.current_page > 1


class EventListFilters(BaseModel):
    """Filters applied to the event listing."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Filters applied to the event listing."},
    )

    tier: str = Field(default="all", description="Tier filter applied")
    region: str = Field(default="all", description="Region filter applied")
    status: str | None = Field(default=None, description="Status filter applied")
    page: int = Field(default=1, description="Page number requested")


class EventList(BaseModel):
    """Paginated list of events from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Paginated list of events from vlr.gg."},
    )

    events: list[EventListItem] = Field(
        default_factory=list, description="List of events on the current page",
    )
    matches: list[EventListItem] = Field(
        default_factory=list,
        description="Alias for events — required for PageProtocol compatibility",
    )
    has_next_page: bool = Field(
        default=False,
        description="Whether a subsequent page exists (derived from pagination)",
    )
    filters: EventListFilters = Field(..., description="Filters applied")
    pagination: EventListPagination = Field(..., description="Pagination metadata")

    @model_validator(mode="after")
    def _sync_matches_and_has_next(self) -> "EventList":
        self.matches = self.events
        self.has_next_page = self.pagination.has_next
        return self
