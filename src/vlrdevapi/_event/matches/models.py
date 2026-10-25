from datetime import date, datetime, time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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
    country_name: str = Field(
        default="",
        description=(
            "Full country name from the team's flag (e.g., 'United States'); "
            "empty for TBD or an unknown flag"
        ),
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


class EventMatches(ExportableModel):
    """Collection of matches for an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of matches for an event."},
    )

    event_id: int = Field(description="Event identifier")
    matches: list[EventMatch] = Field(
        default_factory=list, description="List of matches in the event",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert event matches to tabular records."""
        records: list[dict[str, Any]] = []
        for m in self.matches:
            team1 = m.teams[0] if len(m.teams) > 0 else None
            team2 = m.teams[1] if len(m.teams) > 1 else None
            t1_name = (team1.name if team1 else "") or "TBD"
            t2_name = (team2.name if team2 else "") or "TBD"

            records.append({
                "event_id": self.event_id,
                "match_id": m.match_id,
                "stage": m.stage,
                "phase": m.phase,
                "status": m.status.value if hasattr(m.status, "value") else str(m.status),
                "datetime_utc": m.datetime_utc.isoformat() if m.datetime_utc else None,
                "team1_name": t1_name,
                "team1_id": team1.id if team1 else None,
                "team1_score": team1.score if team1 else None,
                "team1_winner": team1.winner if team1 else False,
                "team2_name": t2_name,
                "team2_id": team2.id if team2 else None,
                "team2_score": team2.score if team2 else None,
                "team2_winner": team2.winner if team2 else False,
                "url": f"https://www.vlr.gg/{m.match_id}",
            })
        return records
