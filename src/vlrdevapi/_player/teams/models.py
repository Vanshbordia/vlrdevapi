
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PlayerTeam(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team entry on a player's profile."},
    )

    team_id: int = Field(description="Team ID on vlr.gg")
    name: str = Field(description="Team name (e.g. 'NRG')")
    slug: str = Field(description="URL slug (e.g. 'nrg')")
    logo_url: str = Field(default="", description="URL to team logo image")
    joined_date: date | None = Field(
        default=None,
        description="Date player joined the team (1st of month)",
    )
    left_date: date | None = Field(
        default=None,
        description="Date player left the team (1st of month)",
    )
    inactive_date: date | None = Field(
        default=None,
        description="Date player became inactive on the team (1st of month)",
    )


class PlayerTeams(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Current and past teams for a player."},
    )

    current_teams: list[PlayerTeam] = Field(
        default_factory=list,
        description="Teams the player is currently on",
    )
    past_teams: list[PlayerTeam] = Field(
        default_factory=list,
        description="Teams the player was on previously",
    )

class PlayerPastTeams(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Past teams for a player."},
    )

    past_teams: list[PlayerTeam] = Field(
        default_factory=list,
        description="Teams the player was on previously",
    )

    def __len__(self) -> int:
        return len(self.past_teams)

    def __iter__(self):  # type: ignore[override]
        return iter(self.past_teams)

    def __getitem__(self, index):
        return self.past_teams[index]
