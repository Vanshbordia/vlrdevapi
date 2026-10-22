
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RoundWinType(StrEnum):
    """How a round was won in a Valorant match."""

    ELIMINATION = "elimination"
    """Round won by eliminating all opponents."""
    DEFUSE = "defuse"
    """Round won by defusing the spike."""
    SPIKE_DETONATION = "spike_detonation"
    """Round won by detonating the spike."""
    TIME_EXPIRED = "time_expired"
    """Round won because the round clock expired."""

    @property
    def full_name(self) -> str:
        """Return the human-readable name for this win type."""
        return {
            "elimination": "Elimination",
            "defuse": "Defuse",
            "spike_detonation": "Spike detonation",
            "time_expired": "Time expired",
        }.get(self.value, self.value)


class RoundData(BaseModel):
    """A single round within a game/map on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single round within a game/map on vlr.gg."},
    )

    round_number: int = Field(default=0, description="Round number in the game")
    winner_team_name: str = Field(default="", description="Winning team name")
    winner_team_id: int = Field(default=0, description="Winning team ID")
    win_type: RoundWinType = Field(
        default=RoundWinType.ELIMINATION,
        description="How the round was won (elimination, defuse, boom, or time)",
    )
    side: str = Field(
        default="",
        description="Actual side the winning team played: Defense (CT) or Attack (T)",
    )
    team1_score: int = Field(
        default=0, description="Team 1's total score after this round",
    )
    team2_score: int = Field(
        default=0, description="Team 2's total score after this round",
    )
    bank_team1: float | None = Field(
        default=None,
        description="Team 1's bank at round start; None when economy data was not merged",
    )
    bank_team2: float | None = Field(
        default=None,
        description="Team 2's bank at round start; None when economy data was not merged",
    )
    spent_team1: int | None = Field(
        default=None,
        description="Money spent by team 1 this round; None when economy data was not merged",
    )
    spent_team2: int | None = Field(
        default=None,
        description="Money spent by team 2 this round; None when economy data was not merged",
    )
    buy_type_team1: str = Field(
        default="",
        description="Team 1 buy tier: 'Pistol', 'Eco', 'Half-buy', or 'Full-buy' (empty when economy data was not merged)",
    )
    buy_type_team2: str = Field(
        default="",
        description="Team 2 buy tier: 'Pistol', 'Eco', 'Half-buy', or 'Full-buy' (empty when economy data was not merged)",
    )
    is_pistol_round: bool = Field(
        default=False,
        description="Whether this is a pistol round (rounds 1 and 13)",
    )


class RoundsData(BaseModel):
    """Round-by-round data for a game/map within a series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Round-by-round data for a game/map within a series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    game_id: int = Field(default=0, description="Unique game identifier on vlr.gg")
    team1: str = Field(default="", description="Team 1 name (first team listed)")
    team1_id: int = Field(default=0, description="Team 1 ID")
    team2: str = Field(default="", description="Team 2 name (second team listed)")
    team2_id: int = Field(default=0, description="Team 2 ID")
    rounds: list[RoundData] = Field(
        default_factory=list,
        description="List of rounds for this game",
    )
