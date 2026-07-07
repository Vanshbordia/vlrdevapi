
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RoundWinType(Enum):
    """How a round was won in a Valorant match."""

    ELIMINATION = "elim"
    """Round won by eliminating all opponents."""
    DEFUSE = "defuse"
    """Round won by defusing the spike."""
    BOOM = "boom"
    """Round won by spike detonation."""
    TIME = "time"
    """Round won by timeout (clock expired)."""

    @property
    def full_name(self) -> str:
        """Return the human-readable name for this win type."""
        return {
            "elim": "Elimination",
            "defuse": "Defuse",
            "boom": "Spike detonation",
            "time": "Time out",
        }.get(self.value, self.value)


class RoundData(BaseModel):
    """A single round within a game/map on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A single round within a game/map on vlr.gg."},
    )

    round_number: int = Field(default=0, description="Round number in the game")
    winner_team_name: str = Field(default="", description="Winning team name")
    winner_team_id: int = Field(default=0, description="Winning team ID")
    win_type: str = Field(default="", description="Type of win")
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
