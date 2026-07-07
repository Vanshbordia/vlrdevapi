
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class BuyType(Enum):
    """Team buy level based on total spending in a round."""

    ECO = "Eco"
    """Eco buy (0-5k total team spend)."""
    SEMI_ECO = "Semi-eco"
    """Semi-eco buy (5-10k total team spend)."""
    SEMI_BUY = "Semi-buy"
    """Semi-buy (10-20k total team spend)."""
    FULL_BUY = "Full-buy"
    """Full buy (20k+ total team spend)."""

    @property
    def display_name(self) -> str:
        """Return the human-readable display name for this buy type."""
        return self.value


class RoundWinner(BaseModel):
    """Winner information for a round."""

    name: str = Field(default="", description="Winning team name")
    id: int = Field(default=0, description="Winning team ID")


class RoundEconomyData(BaseModel):
    """Economy data for a single round within a game/map on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Economy data for a single round within a game/map on vlr.gg.",
        },
        use_enum_values=True,
    )

    _temp_winner: str = PrivateAttr(default="")

    round_number: int = Field(default=0, description="Round number in the game")
    bank_team1: float = Field(default=0.0, description="Bank amount for team 1")
    bank_team2: float = Field(default=0.0, description="Bank amount for team 2")
    spent_team1: int = Field(
        default=0, description="Money spent by team 1 in this round",
    )
    spent_team2: int = Field(
        default=0, description="Money spent by team 2 in this round",
    )
    winner: RoundWinner = Field(
        default_factory=RoundWinner, description="Winning team information",
    )
    buy_type_team1: BuyType = Field(
        default=BuyType.ECO, description="Buy type for team 1",
    )
    buy_type_team2: BuyType = Field(
        default=BuyType.ECO, description="Buy type for team 2",
    )
    is_pistol_round: bool = Field(
        default=False, description="Whether this is a pistol round (rounds 1 and 13)",
    )


class EconomyData(BaseModel):
    """Economy data for a game/map within a series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Economy data for a game/map within a series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    game_id: int = Field(default=0, description="Unique game identifier on vlr.gg")
    team1: str = Field(default="", description="Team 1 name (defense in first half)")
    team1_id: int = Field(default=0, description="Team 1 ID")
    team2: str = Field(default="", description="Team 2 name (attack in first half)")
    team2_id: int = Field(default=0, description="Team 2 ID")
    rounds: list[RoundEconomyData] = Field(
        default_factory=list,
        description="List of economy data for each round",
    )
