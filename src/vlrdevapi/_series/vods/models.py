from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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


class SeriesVods(ExportableModel):
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

    def to_records(self, view: str = "vods", **kwargs: Any) -> list[dict[str, Any]]:
        """Convert VODs or streams to tabular records.

        Args:
            view: Either 'vods' or 'streams'.
        """
        series_url = f"https://www.vlr.gg/{self.series_id}"
        records: list[dict[str, Any]] = []
        if view == "streams":
            for s in self.streams:
                records.append({
                    "series_id": self.series_id,
                    "platform": s.platform,
                    "channel": s.channel,
                    "stream_type": s.stream_type,
                    "country_code": s.country_code,
                    "url": s.url,
                    "series_url": series_url,
                })
        else:
            for v in self.vods:
                records.append({
                    "series_id": self.series_id,
                    "label": v.label,
                    "platform": v.platform,
                    "map_number": v.map_number,
                    "start_seconds": v.start_seconds,
                    "url": v.url,
                    "series_url": series_url,
                })
        return records
