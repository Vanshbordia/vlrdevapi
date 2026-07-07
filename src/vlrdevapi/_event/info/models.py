
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EventSeriesLink(BaseModel):
    """A breadcrumb link above the event title (series/tournament)."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A breadcrumb link above the event title (series/tournament).",
        },
    )

    name: str = Field(
        default="",
        description="Display name (e.g., 'Valorant Champions Tour 2026')",
    )
    href: str = Field(default="", description="Relative path (e.g., '/vct')")


class EventPrize(BaseModel):
    """Prize information for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Prize information for an event."},
    )

    amount: int | None = Field(
        default=None,
        description="Numeric prize amount, None if TBD or not applicable",
    )
    currency_symbol: str | None = Field(
        default=None,
        description="Currency symbol (e.g., '$', '€', '¥'), None if TBD",
    )
    currency_code: str | None = Field(
        default=None,
        description="ISO currency code (e.g., 'USD', 'EUR', 'JPY'), None if TBD",
    )
    converted_amount: int | None = Field(
        default=None,
        description="Converted USD amount if available, None otherwise",
    )
    is_tbd: bool = Field(default=False, description="True if prize is listed as 'TBD'")
    raw_text: str = Field(
        default="",
        description="Raw prize text as displayed on the page (e.g., '¥4,000,000 JPY  ~ $25,656 USD')",
    )


class EventRegion(BaseModel):
    """Region information inferred from breadcrumb tags."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Region information inferred from breadcrumb tags.",
        },
    )

    name: str = Field(
        default="",
        description="Region name (e.g., 'EMEA', 'Pacific', 'Americas', 'China', 'International')",
    )
    href: str = Field(default="", description="Relative path (e.g., '/vct/?region=27')")


class EventStageTag(BaseModel):
    """Stage tag from breadcrumb."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Stage tag from breadcrumb."},
    )

    name: str = Field(default="", description="Stage name (e.g., 'Stage 1')")
    href: str = Field(default="", description="Relative path (e.g., '/vct/?stage=1')")


class EventLocation(BaseModel):
    """Location/venue information for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Location/venue information for an event."},
    )

    country: str = Field(
        default="",
        description="Country name resolved from flag mod-XX class using countries.py",
    )
    venue: str = Field(
        default="",
        description="Venue/location text (e.g., 'Riot Games Arena, Berlin'); empty if only a flag",
    )


class EventInfo(BaseModel):
    """Event information from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Event information from vlr.gg."},
    )

    id: int = Field(default=0, description="Unique event identifier on vlr.gg")
    name: str = Field(default="", description="Event title from h1.event-header-main-title")
    subtitle: str = Field(
        default="",
        description="Event subtitle from h2.event-header-main-desc",
    )
    image_url: str = Field(default="", description="URL to the event thumbnail image")
    series: EventSeriesLink | None = Field(
        default=None,
        description="Parent series/tournament link (e.g., 'Valorant Champions Tour 2026'); None if no breadcrumb",
    )
    stage: EventStageTag | None = Field(
        default=None,
        description="Stage tag (e.g., 'Stage 1'); None if no stage tag",
    )
    regions: list[EventRegion] = Field(
        default_factory=list,
        description="Region tags; multiple means International",
    )
    start_date: date | None = Field(default=None, description="Event start date")
    end_date: date | None = Field(
        default=None,
        description="Event end date (same as start_date for single-day events)",
    )
    prize: EventPrize | None = Field(
        default=None,
        description="Prize information; None if no prize listed",
    )
    location: EventLocation | None = Field(
        default=None,
        description="Location info from 'Location' desc-item; None if no location item",
    )
    region_location: EventLocation | None = Field(
        default=None,
        description="Region info from 'Region' desc-item (flag-only); None if no region item",
    )
