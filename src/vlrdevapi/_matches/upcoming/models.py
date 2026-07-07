
from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class TeamInUpcomingMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team in an upcoming match entry."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name (e.g. 'NRG', 'FNATIC')")
    tag: str = Field(default="", description="Short team tag (e.g. 'NRG', 'FNC')")
    country_name: str = Field(
        default="", description="Full country name (e.g. 'United States')",
    )


class UpcomingMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "An upcoming match from vlr.gg."},
    )

    match_id: int = Field(default=0, description="Unique match identifier on vlr.gg")
    url: str = Field(default="", description="Relative URL to the match page")
    event: str = Field(default="", description="Event/tournament name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Swiss Stage')",
    )
    team1: TeamInUpcomingMatch | None = Field(default=None, description="First team")
    team2: TeamInUpcomingMatch | None = Field(default=None, description="Second team")
    status: str = Field(
        default="", description="Match status (e.g. 'upcoming', 'live')",
    )
    eta: str = Field(default="", description="Time until match starts (e.g. '1h 46m')")
    datetime: datetime_ | None = Field(
        default=None, description="Match datetime in UTC",
    )


class UpcomingMatchesPage(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A page of upcoming matches from vlr.gg."},
    )

    matches: list[UpcomingMatchEntry] = Field(
        default_factory=list, description="List of upcoming match entries",
    )
    has_next_page: bool = Field(
        default=False, description="Whether there is a next page of results",
    )
