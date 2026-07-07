from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MatchStatus(str, Enum):
    """Status of a match in an event."""

    COMPLETED = "completed"
    """Match has been played and finished."""
    LIVE = "live"
    """Match is currently in progress."""
    UPCOMING = "upcoming"
    """Match is scheduled but not yet started."""


class MatchTeam(BaseModel):
    """Team participating in a match."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team participating in a match."},
    )

    id: int | None = Field(
        default=None,
        description="Team ID from vlr.gg, None for TBD",
    )
    name: str = Field(
        default="",
        description="Team name (e.g., 'FNATIC', 'TBD')",
    )
    score: int | None = Field(
        default=None,
        description="Team score, None if not available (upcoming/TBD)",
    )
    winner: bool = Field(
        default=False,
        description="Whether this team won the match",
    )


class EventMatch(BaseModel):
    """Match data from vlr.gg event matches page."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Match data from vlr.gg event matches page."},
    )

    event_id: int = Field(description="Event identifier")
    match_id: int = Field(description="Match identifier from vlr.gg URL")
    stage: str = Field(
        default="",
        description="Stage name (e.g., 'Group Stage', 'Playoffs')",
    )
    phase: str = Field(
        default="",
        description="Phase name (e.g., 'Week 1', 'Upper Round 1')",
    )
    status: MatchStatus = Field(
        description="Match status: completed, live, or upcoming",
    )
    match_date: date | None = Field(default=None, description="Match date")
    match_time: time | None = Field(default=None, description="Match time")
    datetime_utc: datetime | None = Field(
        default=None, description="Match datetime in UTC",
    )
    teams: list[MatchTeam] = Field(
        default_factory=list, description="Teams in the match (typically 2)",
    )


class EventMatches(BaseModel):
    """Collection of matches for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of matches for an event."},
    )

    event_id: int = Field(description="Event identifier")
    matches: list[EventMatch] = Field(
        default_factory=list, description="List of matches in the event",
    )
