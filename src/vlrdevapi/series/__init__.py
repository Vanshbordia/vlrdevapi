"""Series/match-related API endpoints and models."""

from .models import TeamInfo, MapAction, Info, PlayerStats, MapTeamScore, RoundResult, MapPlayers, KillMatrixEntry, PlayerPerformance, MapPerformance
from .info import info
from .matches import matches
from .performance import performance

__all__ = [
    # Models
    "TeamInfo",
    "MapAction",
    "Info",
    "PlayerStats",
    "MapTeamScore",
    "RoundResult",
    "MapPlayers",
    "KillMatrixEntry",
    "PlayerPerformance",
    "MapPerformance",
    # Functions
    "info",
    "matches",
    "performance",
]
