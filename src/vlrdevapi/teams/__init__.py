"""Team-related API endpoints and models."""

from .models import (
    SocialLink,
    PreviousTeam,
    SuccessorTeam,
    RosterMember,
    TeamInfo,
    MatchTeam,
    TeamMatch,
    EventPlacement,
    PlacementDetail,
    PlayerTransaction,
    PreviousPlayer,
)
from .info import info
from .roster import roster
from .matches import upcoming_matches, completed_matches
from .placements import placements
from .transactions import transactions, previous_players

__all__ = [
    # Models
    "SocialLink",
    "PreviousTeam",
    "SuccessorTeam",
    "RosterMember",
    "TeamInfo",
    "MatchTeam",
    "TeamMatch",
    "EventPlacement",
    "PlacementDetail",
    "PlayerTransaction",
    "PreviousPlayer",
    # Functions
    "info",
    "roster",
    "upcoming_matches",
    "completed_matches",
    "placements",
    "transactions",
    "previous_players",
]
