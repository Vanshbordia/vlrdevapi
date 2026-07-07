
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AgentCompositionLevel = Literal["none", "basic", "detailed"]


class CompositionMatchDetails(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Detailed match information for a specific composition.",
        },
    )

    series_id: int = Field(default=0, description="Match/Series ID")
    date: str = Field(default="", description="Match date (YYYY/MM/DD)")
    opponent_id: int = Field(default=0, description="Opponent team ID")
    opponent_name: str = Field(default="", description="Opponent team name")
    opponent_tag: str = Field(default="", description="Opponent team tag")
    team_score: int = Field(default=0, description="This team's score")
    opponent_score: int = Field(default=0, description="Opponent's score")
    is_win: bool = Field(default=False, description="Whether this map was won")
    attack_rounds_won: int = Field(default=0, description="Rounds won on attack side")
    attack_rounds_lost: int = Field(default=0, description="Rounds lost on attack side")
    defense_rounds_won: int = Field(default=0, description="Rounds won on defense side")
    defense_rounds_lost: int = Field(
        default=0, description="Rounds lost on defense side",
    )
    ot_rounds_won: int = Field(default=0, description="Rounds won in overtime")
    ot_rounds_lost: int = Field(default=0, description="Rounds lost in overtime")
    event_id: int = Field(default=0, description="Event ID")
    event_name: str = Field(default="", description="Event name")
    stage: str = Field(default="", description="Stage within event")
    patch: str = Field(default="", description="Patch version")
    series_result: str = Field(
        default="", description="Overall series result (won/lost)",
    )


class AgentComposition(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Agent composition statistics for a map."},
    )

    agents: list[str] = Field(
        default_factory=list,
        description="Agent names (normalized, sorted alphabetically)",
    )
    games_played: int = Field(
        default=0, description="Number of games with this composition",
    )
    wins: int = Field(default=0, description="Wins with this composition")
    losses: int = Field(default=0, description="Losses with this composition")
    win_rate: float = Field(default=0.0, description="Win rate percentage")
    matches: list[CompositionMatchDetails] | None = Field(
        default=None,
        description="Detailed match data (detailed mode only)",
    )


class MapStats(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Statistics for a single map."},
    )

    map_name: str = Field(default="", description="Map name (e.g., Haven, Bind)")
    games_played: int = Field(
        default=0, description="Number of games played on this map",
    )
    win_rate: float | None = Field(
        default=None, description="Win rate percentage (e.g., 33.0 for 33%)",
    )
    wins: int | None = Field(default=None, description="Number of wins")
    losses: int | None = Field(default=None, description="Number of losses")
    attack_first: int | None = Field(default=None, description="Times starting on attack side")
    defense_first: int | None = Field(default=None, description="Times starting on defense side")
    attack_round_win_rate: float | None = Field(
        default=None, description="Attack round win rate percentage",
    )
    attack_rounds_won: int | None = Field(default=None, description="Attack rounds won")
    attack_rounds_lost: int | None = Field(default=None, description="Attack rounds lost")
    defense_round_win_rate: float | None = Field(
        default=None, description="Defense round win rate percentage",
    )
    defense_rounds_won: int | None = Field(default=None, description="Defense rounds won")
    defense_rounds_lost: int | None = Field(default=None, description="Defense rounds lost")
    compositions: list[AgentComposition] | None = Field(
        default=None, description="Agent compositions for this map (if requested)",
    )


class TeamStats(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Collection of map statistics for a team (excludes maps with 0 games).",
        },
    )

    team_id: int = Field(default=0, description="Team ID")
    maps: list[MapStats] = Field(
        default_factory=list,
        description="Map statistics (only maps with games_played > 0)",
    )
