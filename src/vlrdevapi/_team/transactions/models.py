
from datetime import date as date_
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


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

    date: date_ | None = Field(default=None, description="Transaction date")
    action: TransactionAction = Field(description="Transaction action type")
    player: TransactionPlayer = Field(description="Player involved")
    position: str = Field(
        default="", description="Position/role (e.g., Player, Assistant coach)",
    )
    source_url: str = Field(default="", description="Source URL for transaction")


class TeamTransactions(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of transactions for a team."},
    )

    team_id: int = Field(default=0, description="Team ID")
    transactions: list[TeamTransaction] = Field(
        default_factory=list, description="List of transactions",
    )
