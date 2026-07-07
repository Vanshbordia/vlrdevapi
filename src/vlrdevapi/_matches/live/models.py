
from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class TeamInLiveMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team in a live match entry."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name (e.g. 'NRG', 'FNATIC')")
    tag: str = Field(default="", description="Short team tag (e.g. 'NRG', 'FNC')")
    country_name: str = Field(
        default="", description="Full country name (e.g. 'United States')",
    )


class LiveMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A live match from vlr.gg."},
    )

    match_id: int = Field(default=0, description="Unique match identifier on vlr.gg")
    url: str = Field(default="", description="Relative URL to the match page")
    event: str = Field(default="", description="Event/tournament name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Swiss Stage')",
    )
    team1: TeamInLiveMatch | None = Field(default=None, description="First team")
    team2: TeamInLiveMatch | None = Field(default=None, description="Second team")
    status: str = Field(default="", description="Match status (e.g. 'live')")
    datetime: datetime_ | None = Field(
        default=None, description="Match datetime in UTC",
    )


class LiveMatchesPage(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Live matches from vlr.gg."},
    )

    matches: list[LiveMatchEntry] = Field(
        default_factory=list, description="List of live match entries",
    )
