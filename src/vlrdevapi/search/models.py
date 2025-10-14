"""Search-related data models."""

from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class SearchPlayerResult(BaseModel):
    """Player search result."""
    
    model_config = ConfigDict(frozen=True)
    
    player_id: int = Field(description="Player ID")
    url: str = Field(description="Player URL")
    ign: Optional[str] = Field(None, description="In-game name")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Country")
    image_url: Optional[str] = Field(None, description="Player image URL")
    result_type: Literal["player"] = Field(default="player", description="Result type")


class SearchTeamResult(BaseModel):
    """Team search result."""
    
    model_config = ConfigDict(frozen=True)
    
    team_id: int = Field(description="Team ID")
    url: str = Field(description="Team URL")
    name: Optional[str] = Field(None, description="Team name")
    country: Optional[str] = Field(None, description="Country")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    is_inactive: bool = Field(False, description="Whether team is inactive")
    result_type: Literal["team"] = Field(default="team", description="Result type")


class SearchEventResult(BaseModel):
    """Event search result."""
    
    model_config = ConfigDict(frozen=True)
    
    event_id: int = Field(description="Event ID")
    url: str = Field(description="Event URL")
    name: Optional[str] = Field(None, description="Event name")
    date_range: Optional[str] = Field(None, description="Event date range")
    prize: Optional[str] = Field(None, description="Prize pool")
    image_url: Optional[str] = Field(None, description="Event image URL")
    result_type: Literal["event"] = Field(default="event", description="Result type")


class SearchSeriesResult(BaseModel):
    """Series search result."""
    
    model_config = ConfigDict(frozen=True)
    
    series_id: int = Field(description="Series ID")
    url: str = Field(description="Series URL")
    name: Optional[str] = Field(None, description="Series name")
    image_url: Optional[str] = Field(None, description="Series image URL")
    result_type: Literal["series"] = Field(default="series", description="Result type")


class SearchResults(BaseModel):
    """Combined search results."""
    
    model_config = ConfigDict(frozen=True)
    
    query: str = Field(description="Search query")
    total_results: int = Field(description="Total number of results found")
    players: list[SearchPlayerResult] = Field(default_factory=list, description="Player results")
    teams: list[SearchTeamResult] = Field(default_factory=list, description="Team results")
    events: list[SearchEventResult] = Field(default_factory=list, description="Event results")
    series: list[SearchSeriesResult] = Field(default_factory=list, description="Series results")
