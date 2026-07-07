
from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class OpponentInCompletedMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Opponent team in a completed match."},
    )

    id: int = Field(default=0, description="Opponent team ID")
    name: str = Field(default="", description="Opponent team name")
    tag: str = Field(default="", description="Opponent team tag")


class TeamCompletedMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A completed match for a specific team."},
    )

    match_id: int = Field(default=0, description="Match ID")
    url: str = Field(default="", description="Match URL")
    event: str = Field(default="", description="Event name")
    stage: str = Field(default="", description="Stage within event")
    opponent: OpponentInCompletedMatch | None = Field(
        default=None, description="Opponent team",
    )
    team_score: int = Field(default=0, description="This team's score")
    opponent_score: int = Field(default=0, description="Opponent's score")
    is_win: bool = Field(default=False, description="Whether this team won")
    datetime: datetime_ | None = Field(default=None, description="Match datetime (UTC)")


class TeamCompletedMatches(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of completed matches for a team."},
    )

    team_id: int = Field(default=0, description="Team ID")
    matches: list[TeamCompletedMatchEntry] = Field(
        default_factory=list, description="Completed matches",
    )
