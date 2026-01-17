"""Event-related data models."""

from __future__ import annotations

import datetime
from typing import Literal
from enum import Enum
from dataclasses import dataclass, field


# Enums for autocomplete
class EventTier(str, Enum):
    """Event tier options."""
    ALL = "all"
    VCT = "vct"
    VCL = "vcl"
    T3 = "t3"
    GC = "gc"
    CG = "cg"
    OFFSEASON = "offseason"


class EventStatus(str, Enum):
    """Event status filter options."""
    ALL = "all"
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"


# Type aliases for backward compatibility
TierName = Literal["all", "vct", "vcl", "t3", "gc", "cg", "offseason"]
StatusFilter = Literal["all", "upcoming", "ongoing", "completed"]

_TIER_TO_ID: dict[str, str] = {
    "all": "all",
    "vct": "60",
    "vcl": "61",
    "t3": "62",
    "gc": "63",
    "cg": "64",
    "offseason": "67",
}


@dataclass(frozen=True)
class ListEvent:
    """Event summary from events listing."""

    id: int
    name: str
    status: Literal["upcoming", "ongoing", "completed"]
    url: str
    region: str | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    start_text: str | None = None
    end_text: str | None = None
    prize: str | None = None


@dataclass(frozen=True)
class Info:
    """Event header/info details."""

    id: int
    name: str
    subtitle: str | None = None
    date_text: str | None = None
    prize: str | None = None
    location: str | None = None
    regions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MatchTeam:
    """Team in an event match."""

    name: str
    id: int | None = None
    country: str | None = None
    score: int | None = None
    is_winner: bool | None = None


@dataclass(frozen=True)
class Match:
    """Event match entry."""

    match_id: int
    event_id: int
    status: str
    teams: tuple["MatchTeam", "MatchTeam"]
    url: str
    stage: str | None = None
    phase: str | None = None
    date: datetime.date | None = None
    time: str | None = None


@dataclass(frozen=True)
class StageMatches:
    """Match summary for a stage."""

    name: str
    match_count: int
    completed: int
    upcoming: int
    ongoing: int
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None


@dataclass(frozen=True)
class MatchSummary:
    """Event matches summary."""

    event_id: int
    total_matches: int
    completed: int
    upcoming: int
    ongoing: int
    stages: list["StageMatches"] = field(default_factory=list)


@dataclass(frozen=True)
class Team:
    """Team information for an event."""

    id: int
    name: str
    type: str | None = None


@dataclass(frozen=True)
class StandingEntry:
    """Single standing entry."""

    place: str
    prize: str | None = None
    team_id: int | None = None
    team_name: str | None = None
    team_country: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Standings:
    """Event standings."""

    event_id: int
    stage_path: str
    url: str
    entries: list["StandingEntry"] = field(default_factory=list)


@dataclass(frozen=True)
class EventStage:
    """Available stage option for an event matches page."""

    name: str
    series_id: str
    url: str
