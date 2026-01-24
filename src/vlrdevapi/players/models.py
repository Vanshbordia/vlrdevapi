"""Player-related data models."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SocialLink:
    """Player social media link."""

    label: str
    url: str


@dataclass(frozen=True)
class Team:
    """Player team information."""

    role: str
    id: int | None = None
    name: str | None = None
    joined_date: datetime.date | None = None
    left_date: datetime.date | None = None


@dataclass(frozen=True)
class Profile:
    """Player profile information."""

    player_id: int
    handle: str | None = None
    real_name: str | None = None
    country: str | None = None
    avatar_url: str | None = None
    aliases: list[str] | None = None
    socials: list[SocialLink] = field(default_factory=list)
    current_teams: list[Team] = field(default_factory=list)
    past_teams: list[Team] = field(default_factory=list)


@dataclass(frozen=True)
class MatchTeam:
    """Team in a player match."""

    name: str | None = None
    tag: str | None = None
    core: str | None = None


@dataclass(frozen=True)
class Match:
    """Player match entry."""

    match_id: int
    url: str
    player_team: MatchTeam
    opponent_team: MatchTeam
    event: str | None = None
    stage: str | None = None
    phase: str | None = None
    player_score: int | None = None
    opponent_score: int | None = None
    result: str | None = None
    date: datetime.date | None = None
    time: datetime.time | None = None
    time_text: str | None = None


@dataclass(frozen=True)
class AgentStats:
    """Player agent statistics."""

    agent: str | None = None
    agent_image_url: str | None = None
    usage_count: int | None = None
    usage_percent: float | None = None
    rounds_played: int | None = None
    rating: float | None = None
    acs: float | None = None
    kd: float | None = None
    adr: float | None = None
    kast: float | None = None
    kpr: float | None = None
    apr: float | None = None
    fkpr: float | None = None
    fdpr: float | None = None
    kills: int | None = None
    deaths: int | None = None
    assists: int | None = None
    first_kills: int | None = None
    first_deaths: int | None = None
