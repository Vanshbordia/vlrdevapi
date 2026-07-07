
from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class OpponentInUpcomingMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Opponent team in an upcoming match."},
    )

    id: int = Field(default=0, description="Opponent team ID")
    name: str = Field(default="", description="Opponent team name")
    tag: str = Field(default="", description="Opponent team tag")


class TeamUpcomingMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "An upcoming match for a specific team."},
    )

    match_id: int = Field(default=0, description="Match ID")
    url: str = Field(default="", description="Match URL")
    event: str = Field(default="", description="Event name")
    stage: str = Field(default="", description="Stage within event")
    opponent: OpponentInUpcomingMatch | None = Field(
        default=None, description="Opponent team",
    )
    datetime: datetime_ | None = Field(default=None, description="Match datetime (UTC)")


class TeamUpcomingMatches(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of upcoming matches for a team."},
    )

    team_id: int = Field(default=0, description="Team ID")
    matches: list[TeamUpcomingMatchEntry] = Field(
        default_factory=list, description="Upcoming matches",
    )
