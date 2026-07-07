
from datetime import date as date_
from datetime import datetime as datetime_
from datetime import time as time_

from pydantic import BaseModel, ConfigDict, Field


class TeamInMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team in a player match entry."},
    )

    name: str = Field(default="", description="Team name (e.g. 'NRG')")
    tag: str = Field(default="", description="Team tag (e.g. 'NRG')")
    logo_url: str = Field(default="", description="URL to team logo image")


class MatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "A match from a player's match history on vlr.gg.",
        },
    )

    match_id: int = Field(default=0, description="Unique match identifier on vlr.gg")
    url: str = Field(default="", description="Relative URL to the match page")
    event: str = Field(default="", description="Event/tournament name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Swiss Stage')",
    )
    bracket: str = Field(
        default="", description="Bracket/round within the stage (e.g. 'LBF', 'GF')",
    )
    team1: TeamInMatch = Field(default_factory=TeamInMatch, description="First team")
    team2: TeamInMatch = Field(default_factory=TeamInMatch, description="Second team")
    score1: int = Field(default=0, description="Score of the first team")
    score2: int = Field(default=0, description="Score of the second team")
    result: str = Field(
        default="", description="Match result for the player ('win' or 'loss')",
    )
    date: date_ | None = Field(default=None, description="Match date")
    time: time_ | None = Field(default=None, description="Match time")
    datetime: datetime_ | None = Field(
        default=None, description="Combined match datetime in UTC",
    )


class MatchHistoryPage(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "A page of matches from a player's match history on vlr.gg.",
        },
    )

    matches: list[MatchEntry] = Field(
        default_factory=list, description="List of match entries on this page",
    )
    has_next_page: bool = Field(
        default=False, description="Whether there is a next page of results",
    )

class PlayerMatches(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Collection of match entries for a player.",
        },
    )

    player_id: int = Field(description="Unique player identifier on vlr.gg")
    matches: list[MatchEntry] = Field(
        default_factory=list, description="List of match entries",
    )

    def __len__(self) -> int:
        return len(self.matches)

    def __iter__(self):  # type: ignore[override]
        return iter(self.matches)

    def __getitem__(self, index):
        return self.matches[index]
