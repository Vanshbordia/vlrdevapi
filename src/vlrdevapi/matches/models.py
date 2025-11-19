"""Match-related data models."""

from __future__ import annotations

import datetime
from typing import Literal
from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    """Represents a team in a match."""

    name: str
    id: int | None = None
    country: str | None = None
    score: int | None = None


@dataclass(frozen=True)
class Match:
    """Represents a match summary."""

    match_id: int
    team1: Team
    team2: Team
    event_phase: str
    event: str
    time: str
    status: Literal["upcoming", "live", "completed"]
    date: datetime.date | None = None
