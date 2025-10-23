"""Search-related data models."""

from __future__ import annotations

from typing import Literal
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SearchPlayerResult:
    """Player search result."""

    player_id: int
    url: str
    ign: str | None = None
    real_name: str | None = None
    country: str | None = None
    image_url: str | None = None
    result_type: Literal["player"] = "player"


@dataclass(frozen=True)
class SearchTeamResult:
    """Team search result."""

    team_id: int
    url: str
    name: str | None = None
    country: str | None = None
    logo_url: str | None = None
    is_inactive: bool = False
    result_type: Literal["team"] = "team"


@dataclass(frozen=True)
class SearchEventResult:
    """Event search result."""

    event_id: int
    url: str
    name: str | None = None
    date_range: str | None = None
    prize: str | None = None
    image_url: str | None = None
    result_type: Literal["event"] = "event"


@dataclass(frozen=True)
class SearchSeriesResult:
    """Series search result."""

    series_id: int
    url: str
    name: str | None = None
    image_url: str | None = None
    result_type: Literal["series"] = "series"


@dataclass(frozen=True)
class SearchResults:
    """Combined search results."""

    query: str
    total_results: int
    players: list[SearchPlayerResult] = field(default_factory=list)
    teams: list[SearchTeamResult] = field(default_factory=list)
    events: list[SearchEventResult] = field(default_factory=list)
    series: list[SearchSeriesResult] = field(default_factory=list)
