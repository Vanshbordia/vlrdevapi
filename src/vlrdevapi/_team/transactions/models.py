
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class TransactionAction(str, Enum):
    """Type of roster transaction."""

    Join = "Join"
    """Player joined the team."""
    Leave = "Leave"
    """Player left the team."""
    Inactive = "Inactive"
    """Player moved to inactive/bench status."""


class TransactionPlayer(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Player involved in a transaction."},
    )

    id: int = Field(default=0, description="Player ID on vlr.gg")
    ign: str = Field(default="", description="In-game name")
    real_name: str = Field(default="", description="Real name")
    country: str = Field(default="", description="Country name")


class TeamTransaction(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team transaction entry."},
    )

    date: datetime | None = Field(default=None, description="Transaction date in UTC")
    action: TransactionAction = Field(description="Transaction action type")
    player: TransactionPlayer = Field(description="Player involved")
    position: str = Field(
        default="", description="Position/role (e.g., Player, Assistant coach)",
    )
    source_url: str = Field(default="", description="Source URL for transaction")


class TeamTransactions(ExportableModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of transactions for a team."},
    )

    team_id: int = Field(default=0, description="Team ID")
    transactions: list[TeamTransaction] = Field(
        default_factory=list, description="List of transactions",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten roster transactions into tabular records (1 row per transaction)."""
        records: list[dict[str, Any]] = []
        for t in self.transactions:
            act = t.action.value if hasattr(t.action, "value") else str(t.action)
            records.append({
                "team_id": self.team_id,
                "date": t.date.isoformat() if t.date else None,
                "action": act,
                "player_id": t.player.id or None,
                "ign": t.player.ign,
                "real_name": t.player.real_name,
                "country": t.player.country,
                "position": t.position,
                "source_url": t.source_url,
                "player_url": f"https://www.vlr.gg/player/{t.player.id}" if t.player and t.player.id else "",
            })
        return records
