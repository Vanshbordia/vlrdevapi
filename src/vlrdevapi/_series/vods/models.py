from pydantic import BaseModel, ConfigDict, Field


class SeriesStream(BaseModel):
    """A live or watch-party stream linked from a series match."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A live or watch-party stream linked from a series match.",
        },
    )

    platform: str = Field(
        default="",
        description="Streaming platform code (e.g. 'twitch', 'youtube', 'bilibili')",
    )
    channel: str = Field(default="", description="Channel or display name")
    url: str = Field(default="", description="Full URL to the stream")
    stream_type: str = Field(
        default="broadcast",
        description="Stream kind: 'broadcast' or 'watchparty'",
    )
    country_code: str = Field(
        default="", description="Country/language hint from the flag (e.g. 'us', 'cn')",
    )


class SeriesVod(BaseModel):
    """A single VOD/video link for a series match."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single VOD/video link for a series match."},
    )

    url: str = Field(default="", description="Full URL to the VOD")
    label: str = Field(
        default="", description="Display label (e.g. 'Full match', 'Map 1')",
    )
    platform: str = Field(
        default="", description="Platform code (e.g. 'twitch', 'youtube')",
    )
    map_number: int | None = Field(
        default=None, description="Map number for map-specific VODs, None for full match",
    )
    start_seconds: int | None = Field(
        default=None, description="Start offset into the video in seconds",
    )


class SeriesVods(BaseModel):
    """Streams and VOD/video links for a match/series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Streams and VOD/video links for a match/series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    streams: list[SeriesStream] = Field(
        default_factory=list, description="Live and watch-party streams",
    )
    vods: list[SeriesVod] = Field(default_factory=list, description="List of VOD entries")
