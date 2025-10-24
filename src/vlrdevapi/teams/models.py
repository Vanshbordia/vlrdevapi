"""Team-related data models."""

from __future__ import annotations

from datetime import datetime
from datetime import date as date_type
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SocialLink:
    """Team social media link."""

    label: str
    url: str


@dataclass(frozen=True)
class PreviousTeam:
    """Information about a team's previous name/identity."""

    team_id: int | None = None
    name: str | None = None


@dataclass(frozen=True)
class SuccessorTeam:
    """Information about a team's successor/current banner identity."""

    team_id: int | None = None
    name: str | None = None


@dataclass(frozen=True)
class RosterMember:
    """Team roster member (player or staff)."""

    role: str
    player_id: int | None = None
    ign: str | None = None
    real_name: str | None = None
    country: str | None = None
    is_captain: bool = False
    photo_url: str | None = None


@dataclass(frozen=True)
class TeamInfo:
    """Team information."""

    team_id: int
    name: str | None = None
    tag: str | None = None
    logo_url: str | None = None
    country: str | None = None
    is_active: bool = True
    socials: list[SocialLink] = field(default_factory=list)
    previous_team: PreviousTeam | None = None
    current_team: SuccessorTeam | None = None


@dataclass(frozen=True)
class MatchTeam:
    """Team information in a match context."""

    team_id: int | None = None
    name: str | None = None
    tag: str | None = None
    logo: str | None = None
    score: int | None = None


@dataclass(frozen=True)
class TeamMatch:
    """Team match information."""

    team1: MatchTeam
    team2: MatchTeam
    match_id: int | None = None
    match_url: str | None = None
    tournament_name: str | None = None
    phase: str | None = None
    series: str | None = None
    match_datetime: datetime | None = None


@dataclass(frozen=True)
class PlacementDetail:
    """Individual placement detail within an event.""" 

    series: str | None = None
    place: str | None = None
    prize_money: str | None = None


@dataclass(frozen=True)
class EventPlacement:
    """Team event placement information."""

    event_id: int | None = None
    event_name: str | None = None
    event_url: str | None = None
    placements: list[PlacementDetail] = field(default_factory=list)
    year: str | None = None


@dataclass(frozen=True)
class PlayerTransaction:
    """Individual player transaction record."""

    date: date_type | None = None
    action: str | None = None
    player_id: int | None = None
    ign: str | None = None
    real_name: str | None = None
    country: str | None = None
    position: str | None = None
    reference_url: str | None = None


@dataclass(frozen=True)
class PreviousPlayer:
    """Previous player with calculated status."""

    status: str
    player_id: int | None = None
    ign: str | None = None
    real_name: str | None = None
    country: str | None = None
    position: str | None = None
    join_date: date_type | None = None
    leave_date: date_type | None = None
    transactions: list[PlayerTransaction] = field(default_factory=list)
