"""Team-related API endpoints and models."""

from .models import (
    SocialLink,
    PreviousTeam,
    RosterMember,
    TeamInfo,
    TeamMatch,
    EventPlacement,
    PlacementDetail,
)
from .info import info
from .roster import roster
from .matches import upcoming_matches, completed_matches
from .placements import placements

__all__ = [
    # Models
    "SocialLink",
    "PreviousTeam",
    "RosterMember",
    "TeamInfo",
    "TeamMatch",
    "EventPlacement",
    "PlacementDetail",
    # Functions
    "info",
    "roster",
    "upcoming_matches",
    "completed_matches",
    "placements",
]
