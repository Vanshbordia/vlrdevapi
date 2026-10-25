
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class Player(BaseModel):
    """Player or staff member information."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Player or staff member information."},
    )

    id: int = Field(description="Unique player identifier on vlr.gg")
    ign: str = Field(default="", description="In-game name")
    real_name: str = Field(default="", description="Real name")
    country: str = Field(default="", description="Country name")
    roles: list[str] = Field(
        default_factory=list,
        description="List of roles (e.g., ['Player'], ['Head Coach'])",
    )
    is_captain: bool = Field(
        default=False, description="Whether the player is team captain",
    )
    photo_url: str = Field(default="", description="Photo URL")
    is_active: bool = Field(default=True, description="Whether the player is active")
    is_sub: bool = Field(
        default=False, description="Whether the player is a substitute",
    )


class TeamRoster(ExportableModel):
    """Team roster information from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team roster information from vlr.gg."},
    )

    players: list[Player] = Field(default_factory=list, description="List of players")
    staff: list[Player] = Field(
        default_factory=list, description="List of staff members",
    )

    def to_records(self, include_staff: bool = True, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten roster into tabular records (1 row per member)."""
        records: list[dict[str, Any]] = []
        members = list(self.players) + (list(self.staff) if include_staff else [])
        for m in members:
            records.append({
                "player_id": m.id,
                "ign": m.ign,
                "real_name": m.real_name or None,
                "country": m.country or None,
                "primary_role": m.roles[0] if m.roles else None,
                "roles": list(m.roles) if m.roles else [],
                "is_captain": m.is_captain,
                "is_active": m.is_active,
                "is_sub": m.is_sub,
                "photo_url": m.photo_url or None,
                "url": f"https://www.vlr.gg/player/{m.id}",
            })
        return records
