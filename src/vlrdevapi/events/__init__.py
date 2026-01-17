"""Event-related API endpoints and models.

This module provides access to:
- events.list_events(): List all events with filters
- events.Info: Get event header/info
- events.Matches: Get event matches
- events.MatchSummary: Get event matches summary
- events.Standings: Get event standings
- events.Teams: Get event teams
"""

from .models import (
    EventTier,
    EventStatus,
    TierName,
    StatusFilter,
    ListEvent,
    Info,
    MatchTeam,
    Match,
    StageMatches,
    MatchSummary,
    StandingEntry,
    Standings,
    EventStage,
    Team,
)
from .list_events import list_events
from .info import info
from .matches import matches
from .match_summary import match_summary
from .standings import standings
from .stages import stages
from .teams import teams

__all__ = [
    # Enums
    "EventTier",
    "EventStatus",
    # Type aliases
    "TierName",
    "StatusFilter",
    # Models
    "ListEvent",
    "Info",
    "MatchTeam",
    "Match",
    "StageMatches",
    "MatchSummary",
    "StandingEntry",
    "Standings",
    "EventStage",
    "Team",
    # Functions
    "list_events",
    "info",
    "matches",
    "match_summary",
    "standings",
    "stages",
    "teams",
]
