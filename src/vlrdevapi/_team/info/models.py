from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class TeamSocial(BaseModel):
    """Team social media information."""

    name: str = Field(description="Platform name (e.g., 'Twitch', 'YouTube')")
    url: str = Field(description="Full URL to the social media profile")


class TeamSuccessor(BaseModel):
    """Team successor information."""

    id: int = Field(description="Team ID")
    name: str = Field(description="Team name")


class TeamInfo(ExportableModel):
    """Team information from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team information from vlr.gg."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name")
    tag: str = Field(default="", description="Short team tag")
    light_logo_url: str = Field(
        default="", description="URL to the team light logo image",
    )
    dark_logo_url: str = Field(
        default="", description="URL to the team dark logo image",
    )
    country: str = Field(default="", description="Team country name")
    is_active: bool = Field(default=True, description="Whether the team is active")
    socials: list[TeamSocial] | None = Field(
        default=None, description="List of team social media profiles",
    )
    previous_teams: list[TeamSuccessor] | None = Field(
        default=None, description="List of previous team names/IDs",
    )
    current_teams: list[TeamSuccessor] | None = Field(
        default=None, description="List of current team names/IDs",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten team info into a clean scalar tabular record."""
        socials_data = [{"name": s.name, "url": s.url} for s in self.socials] if self.socials else None
        prev_teams_data = [{"id": t.id, "name": t.name} for t in self.previous_teams] if self.previous_teams else None
        curr_teams_data = [{"id": t.id, "name": t.name} for t in self.current_teams] if self.current_teams else None
        return [{
            "team_id": self.id,
            "name": self.name,
            "tag": self.tag or None,
            "country": self.country or None,
            "is_active": self.is_active,
            "url": f"https://www.vlr.gg/team/{self.id}",
            "socials": socials_data,
            "previous_teams": prev_teams_data,
            "current_teams": curr_teams_data,
            "light_logo_url": self.light_logo_url or None,
            "dark_logo_url": self.dark_logo_url or None,
        }]
