"""Team-related data models."""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from datetime import date as date_type
from pydantic import BaseModel, Field, ConfigDict


class SocialLink(BaseModel):
    """Team social media link."""
    
    model_config = ConfigDict(frozen=True)
    
    label: str = Field(description="Link label")
    url: str = Field(description="Link URL")


class PreviousTeam(BaseModel):
    """Information about a team's previous name/identity."""
    
    model_config = ConfigDict(frozen=True)
    
    team_id: Optional[int] = Field(None, description="Previous team ID")
    name: Optional[str] = Field(None, description="Previous team name")


class SuccessorTeam(BaseModel):
    """Information about a team's successor/current banner identity."""
    
    model_config = ConfigDict(frozen=True)
    
    team_id: Optional[int] = Field(None, description="Successor team ID")
    name: Optional[str] = Field(None, description="Successor team name")


class RosterMember(BaseModel):
    """Team roster member (player or staff)."""
    
    model_config = ConfigDict(frozen=True)
    
    player_id: Optional[int] = Field(None, description="Player ID")
    ign: Optional[str] = Field(None, description="In-game name")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Country")
    role: str = Field(description="Role (e.g., Player, Head Coach, Sub)")
    is_captain: bool = Field(False, description="Whether player is team captain")
    photo_url: Optional[str] = Field(None, description="Player photo URL")


class TeamInfo(BaseModel):
    """Team information."""
    
    model_config = ConfigDict(frozen=True)
    
    team_id: int = Field(description="Team ID")
    name: Optional[str] = Field(None, description="Team name")
    tag: Optional[str] = Field(None, description="Team tag/short name")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    country: Optional[str] = Field(None, description="Country")
    is_active: bool = Field(True, description="Whether team is active")
    socials: List[SocialLink] = Field(default_factory=list, description="Social media links")
    previous_team: Optional[PreviousTeam] = Field(None, description="Previous team identity if renamed")
    current_team: Optional[SuccessorTeam] = Field(None, description="If inactive, team currently playing under this banner")


class MatchTeam(BaseModel):
    """Team information in a match context."""
    
    model_config = ConfigDict(frozen=True)
    
    team_id: Optional[int] = Field(None, description="Team ID")
    name: Optional[str] = Field(None, description="Team name")
    tag: Optional[str] = Field(None, description="Team tag/short name")
    logo: Optional[str] = Field(None, description="Team logo URL")
    score: Optional[int] = Field(None, description="Team score")


class TeamMatch(BaseModel):
    """Team match information."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: Optional[int] = Field(None, description="Match ID")
    match_url: Optional[str] = Field(None, description="Match URL")
    tournament_name: Optional[str] = Field(None, description="Tournament name")
    phase: Optional[str] = Field(None, description="Tournament phase (e.g., 'Playoffs')")
    series: Optional[str] = Field(None, description="Series (e.g., 'GF', 'Semi Finals')")
    team1: MatchTeam = Field(description="First team information")
    team2: MatchTeam = Field(description="Second team information")
    match_datetime: Optional[datetime] = Field(None, description="Match date and time")


class PlacementDetail(BaseModel):
    """Individual placement detail within an event."""
    
    model_config = ConfigDict(frozen=True)
    
    series: Optional[str] = Field(None, description="Series/stage (e.g., 'Playoffs', '#5')")
    place: Optional[str] = Field(None, description="Placement (e.g., '1st', '3rd-4th')")
    prize_money: Optional[str] = Field(None, description="Prize money (e.g., '$28,256')")


class EventPlacement(BaseModel):
    """Team event placement information."""
    
    model_config = ConfigDict(frozen=True)
    
    event_id: Optional[int] = Field(None, description="Event ID")
    event_name: Optional[str] = Field(None, description="Event name")
    event_url: Optional[str] = Field(None, description="Event URL")
    placements: List[PlacementDetail] = Field(default_factory=list, description="List of placements in this event")
    year: Optional[str] = Field(None, description="Year of the event")


class PlayerTransaction(BaseModel):
    """Individual player transaction record."""
    
    model_config = ConfigDict(frozen=True)
    
    date: Optional[date_type] = Field(None, description="Transaction date")
    action: Optional[str] = Field(None, description="Action type (join, leave, inactive, etc.)")
    player_id: Optional[int] = Field(None, description="Player ID")
    ign: Optional[str] = Field(None, description="In-game name")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Country")
    position: Optional[str] = Field(None, description="Position/role (Player, Head Coach, etc.)")
    reference_url: Optional[str] = Field(None, description="Reference URL for transaction")


class PreviousPlayer(BaseModel):
    """Previous player with calculated status."""
    
    model_config = ConfigDict(frozen=True)
    
    player_id: Optional[int] = Field(None, description="Player ID")
    ign: Optional[str] = Field(None, description="In-game name")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Country")
    position: Optional[str] = Field(None, description="Position/role")
    status: str = Field(description="Player status (Active, Left, Inactive, Unknown)")
    join_date: Optional[date_type] = Field(None, description="Date joined team")
    leave_date: Optional[date_type] = Field(None, description="Date left team")
    transactions: List[PlayerTransaction] = Field(default_factory=list, description="All transactions for this player")
