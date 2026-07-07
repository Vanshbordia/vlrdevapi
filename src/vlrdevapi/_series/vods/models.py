
from pydantic import BaseModel, ConfigDict, Field


class SeriesVod(BaseModel):
    """A single VOD/video link for a series match."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single VOD/video link for a series match."},
    )

    url: str = Field(default="", description="Full URL to the VOD")
    label: str = Field(
        default="", description="Display label (e.g. 'Full Match', 'Map 1')",
    )


class SeriesVods(BaseModel):
    """VOD/video links for a match/series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "VOD/video links for a match/series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    vods: list[SeriesVod] = Field(default=[], description="List of VOD entries")
