
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class BuyType(Enum):
    """Team buy level based on total spending in a round.

    Eco (under 10k), Half-buy (10k-18k), and Full-buy (18k+). Pistol
    rounds are tracked separately (rounds 1 and 13).
    """

    PISTOL = "Pistol"
    """Pistol round buy (rounds 1 and 13)."""
    ECO = "Eco"
    """Eco buy (total team spend under 10k)."""
    HALF_BUY = "Half-buy"
    """Half buy (total team spend 10k-18k)."""
    FULL_BUY = "Full-buy"
    """Full buy (total team spend 18k+)."""

    @property
    def display_name(self) -> str:
        """Return the human-readable display name for this buy type."""
        return self.value


class RoundWinner(BaseModel):
    """Winner information for a round."""

    name: str = Field(default="", description="Winning team name")
    id: int = Field(default=0, description="Winning team ID")


class EconScore(BaseModel):
    """Won/total record for a single cell of the buy-type matrix."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Won/total record for a single economy matrix cell.",
        },
    )

    won: int = Field(default=0, description="Rounds won")
    total: int = Field(default=0, description="Total rounds played")


class BuyTierRecord(BaseModel):
    """Rounds played on one buy tier, split by the opponent's buy tier.

    Each ``vs_*`` cell shows a ``won``/``total`` record against opponents
    on that tier; ``None`` means the matchup never happened. Use the
    ``total`` property for the combined record across all opponent tiers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Rounds won/total on one buy tier vs each opponent tier.",
        },
    )

    vs_eco: EconScore | None = Field(
        default=None, description="Rounds against opponents on eco.",
    )
    vs_half: EconScore | None = Field(
        default=None, description="Rounds against opponents on half buy.",
    )
    vs_full: EconScore | None = Field(
        default=None, description="Rounds against opponents on full buy.",
    )

    @property
    def total(self) -> EconScore | None:
        """Combined won/total on this tier across every opponent tier.

        Returns:
            ``EconScore`` summing all populated ``vs_*`` cells, or ``None``
            when no opponent-tier matchup was recorded.
        """
        parts = [s for s in (self.vs_eco, self.vs_half, self.vs_full) if s is not None]
        if not parts:
            return None
        return EconScore(
            won=sum(p.won for p in parts),
            total=sum(p.total for p in parts),
        )


class TeamBuyMatrix(BaseModel):
    """Full buy-type matrix for one team.

    ``pistol`` / ``converted`` / ``bonus`` summarize pistol rounds, the
    rounds after pistol wins (conversions), and the rounds after
    conversions (bonus). ``on_eco`` / ``on_half_buy`` / ``on_full_buy``
    hold each tier's record split by the opponent's buy tier; the
    ``eco`` / ``half_buy`` / ``full_buy`` properties are short aliases
    for the same records.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Buy-type matrix for one team.",
        },
    )

    pistol: EconScore | None = Field(
        default=None, description="Pistol rounds won/total.",
    )
    converted: EconScore | None = Field(
        default=None, description="Rounds after pistol (conversion) won/total.",
    )
    bonus: EconScore | None = Field(
        default=None, description="Rounds after conversion (bonus) won/total.",
    )
    on_eco: BuyTierRecord | None = Field(
        default=None, description="Round record while on eco, split by opponent buy type.",
    )
    on_half_buy: BuyTierRecord | None = Field(
        default=None, description="Round record while on half buy, split by opponent buy type.",
    )
    on_full_buy: BuyTierRecord | None = Field(
        default=None, description="Round record while on full buy, split by opponent buy type.",
    )

    @property
    def eco(self) -> BuyTierRecord | None:
        """Alias for ``on_eco``."""
        return self.on_eco

    @property
    def half_buy(self) -> BuyTierRecord | None:
        """Alias for ``on_half_buy``."""
        return self.on_half_buy

    @property
    def full_buy(self) -> BuyTierRecord | None:
        """Alias for ``on_full_buy``."""
        return self.on_full_buy


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
    buy_matrix_team1: TeamBuyMatrix = Field(
        default_factory=TeamBuyMatrix,
        description="Full buy-type matrix for team 1 (summary + per-tier records).",
    )
    buy_matrix_team2: TeamBuyMatrix = Field(
        default_factory=TeamBuyMatrix,
        description="Full buy-type matrix for team 2 (summary + per-tier records).",
    )
    pistol_team1: EconScore | None = Field(
        default=None, description="Pistol rounds won/total for team 1 (shortcut to buy_matrix_team1.pistol).",
    )
    converted_team1: EconScore | None = Field(
        default=None, description="Conversion rounds won/total for team 1 (shortcut to buy_matrix_team1.converted).",
    )
    bonus_team1: EconScore | None = Field(
        default=None, description="Bonus rounds won/total for team 1 (shortcut to buy_matrix_team1.bonus).",
    )
    pistol_team2: EconScore | None = Field(
        default=None, description="Pistol rounds won/total for team 2 (shortcut to buy_matrix_team2.pistol).",
    )
    converted_team2: EconScore | None = Field(
        default=None, description="Conversion rounds won/total for team 2 (shortcut to buy_matrix_team2.converted).",
    )
    bonus_team2: EconScore | None = Field(
        default=None, description="Bonus rounds won/total for team 2 (shortcut to buy_matrix_team2.bonus).",
    )
