"""Series-related data models."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TeamInfo:
    """Team information in a series."""

    name: str
    id: int | None = None
    short: str | None = None
    country: str | None = None
    country_code: str | None = None
    score: int | None = None


@dataclass(frozen=True)
class MapAction:
    """Map pick/ban action."""

    action: str
    team: str
    map: str


@dataclass(frozen=True)
class Info:
    """Series information."""

    match_id: int
    teams: tuple["TeamInfo", "TeamInfo"]
    score: tuple[int | None, int | None]
    status_note: str
    event: str
    event_phase: str
    best_of: str | None = None
    date: datetime.date | None = None
    time: datetime.time | None = None
    patch: str | None = None
    map_actions: list["MapAction"] = field(default_factory=list)
    picks: list["MapAction"] = field(default_factory=list)
    bans: list["MapAction"] = field(default_factory=list)
    remaining: str | None = None


@dataclass(frozen=True)
class PlayerStats:
    """Player statistics in a map."""

    name: str
    country: str | None = None
    team_short: str | None = None
    team_id: int | None = None
    player_id: int | None = None
    agents: list[str] = field(default_factory=list)
    r: float | None = None
    acs: int | None = None
    k: int | None = None
    d: int | None = None
    a: int | None = None
    kd_diff: int | None = None
    kast: float | None = None
    adr: float | None = None
    hs_pct: float | None = None
    fk: int | None = None
    fd: int | None = None
    fk_diff: int | None = None


@dataclass(frozen=True)
class MapTeamScore:
    """Team score for a specific map."""

    is_winner: bool
    id: int | None = None
    name: str | None = None
    short: str | None = None
    score: int | None = None
    attacker_rounds: int | None = None
    defender_rounds: int | None = None


@dataclass(frozen=True)
class RoundResult:
    """Single round result."""

    number: int
    winner_side: str | None = None
    method: str | None = None
    score: tuple[int, int] | None = None
    winner_team_id: int | None = None
    winner_team_short: str | None = None
    winner_team_name: str | None = None


@dataclass(frozen=True)
class MapPlayers:
    """Map statistics with player data."""

    game_id: int | str | None = None
    map_name: str | None = None
    players: list["PlayerStats"] = field(default_factory=list)
    teams: tuple["MapTeamScore", "MapTeamScore"] | None = None
    rounds: list["RoundResult"] | None = None
