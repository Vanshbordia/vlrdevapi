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


@dataclass(frozen=True)
class KillMatrixEntry:
    """Single entry in a kill matrix showing kills between two players."""

    killer_name: str
    victim_name: str
    killer_team_short: str | None = None
    killer_team_id: int | None = None
    victim_team_short: str | None = None
    victim_team_id: int | None = None
    kills: int | None = None
    deaths: int | None = None
    differential: int | None = None


@dataclass(frozen=True)
class MultiKillDetail:
    """Detailed information about a multi-kill event."""

    round_number: int
    players_killed: list[str]


@dataclass(frozen=True)
class ClutchDetail:
    """Detailed information about a clutch event."""

    round_number: int
    players_killed: list[str]


@dataclass(frozen=True)
class PlayerPerformance:
    """Player performance statistics including multi-kills, clutches, and economy."""

    name: str
    team_short: str | None = None
    team_id: int | None = None
    agent: str | None = None
    multi_2k: int | None = None
    multi_3k: int | None = None
    multi_4k: int | None = None
    multi_5k: int | None = None
    clutch_1v1: int | None = None
    clutch_1v2: int | None = None
    clutch_1v3: int | None = None
    clutch_1v4: int | None = None
    clutch_1v5: int | None = None
    econ: int | None = None
    plants: int | None = None
    defuses: int | None = None
    # Detailed information for multi-kills and clutches
    multi_2k_details: list[MultiKillDetail] | None = None
    multi_3k_details: list[MultiKillDetail] | None = None
    multi_4k_details: list[MultiKillDetail] | None = None
    multi_5k_details: list[MultiKillDetail] | None = None
    clutch_1v1_details: list[ClutchDetail] | None = None
    clutch_1v2_details: list[ClutchDetail] | None = None
    clutch_1v3_details: list[ClutchDetail] | None = None
    clutch_1v4_details: list[ClutchDetail] | None = None
    clutch_1v5_details: list[ClutchDetail] | None = None


@dataclass(frozen=True)
class MapPerformance:
    """Performance statistics for a single map/game."""

    game_id: int | str | None = None
    map_name: str | None = None
    kill_matrix: list["KillMatrixEntry"] = field(default_factory=list)
    fkfd_matrix: list["KillMatrixEntry"] = field(default_factory=list)
    op_matrix: list["KillMatrixEntry"] = field(default_factory=list)
    player_performances: list["PlayerPerformance"] = field(default_factory=list)
