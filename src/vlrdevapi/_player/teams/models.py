
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class PlayerTeam(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team entry on a player's profile."},
    )

    team_id: int = Field(description="Team ID on vlr.gg")
    name: str = Field(description="Team name (e.g. 'NRG')")
    slug: str = Field(description="URL slug (e.g. 'nrg')")
    logo_url: str = Field(default="", description="URL to team logo image")
    joined_date: datetime | None = Field(
        default=None,
        description="Date player joined the team in UTC (1st of month)",
    )
    left_date: datetime | None = Field(
        default=None,
        description="Date player left the team in UTC (1st of month)",
    )
    inactive_date: datetime | None = Field(
        default=None,
        description="Date player became inactive in UTC (1st of month)",
    )


class PlayerTeams(ExportableModel):
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

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert current and past teams to tabular records."""
        records: list[dict[str, Any]] = []
        for t in self.current_teams:
            records.append({
                "status": "current",
                "team_id": t.team_id,
                "team_name": t.name or "TBD",
                "slug": t.slug,
                "joined_date": t.joined_date.isoformat() if t.joined_date else None,
                "left_date": t.left_date.isoformat() if t.left_date else None,
                "inactive_date": t.inactive_date.isoformat() if t.inactive_date else None,
                "url": f"https://www.vlr.gg/team/{t.team_id}",
            })
        for t in self.past_teams:
            records.append({
                "status": "past",
                "team_id": t.team_id,
                "team_name": t.name or "TBD",
                "slug": t.slug,
                "joined_date": t.joined_date.isoformat() if t.joined_date else None,
                "left_date": t.left_date.isoformat() if t.left_date else None,
                "inactive_date": t.inactive_date.isoformat() if t.inactive_date else None,
                "url": f"https://www.vlr.gg/team/{t.team_id}",
            })
        return records

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
