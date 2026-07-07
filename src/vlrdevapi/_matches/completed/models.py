
from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class TeamInCompletedMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team in a completed match entry."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name (e.g. 'NRG', 'FNATIC')")
    tag: str = Field(default="", description="Short team tag (e.g. 'NRG', 'FNC')")
    country_name: str = Field(
        default="", description="Full country name (e.g. 'United States')",
    )
    score: int = Field(default=0, description="Number of maps won by the team")
    is_winner: bool = Field(
        default=False, description="Whether this team won the match",
    )


class CompletedMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A completed match from vlr.gg."},
    )

    match_id: int = Field(default=0, description="Unique match identifier on vlr.gg")
    url: str = Field(default="", description="Relative URL to the match page")
    event: str = Field(default="", description="Event/tournament name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Swiss Stage')",
    )
    team1: TeamInCompletedMatch | None = Field(default=None, description="First team")
    team2: TeamInCompletedMatch | None = Field(default=None, description="Second team")
    status: str = Field(default="", description="Match status (e.g. 'completed')")
    datetime: datetime_ | None = Field(
        default=None, description="Match datetime in UTC",
    )


class CompletedMatchesPage(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A page of completed matches from vlr.gg."},
    )

    matches: list[CompletedMatchEntry] = Field(
        default_factory=list, description="List of completed match entries",
    )
    has_next_page: bool = Field(
        default=False, description="Whether there is a next page of results",
    )
