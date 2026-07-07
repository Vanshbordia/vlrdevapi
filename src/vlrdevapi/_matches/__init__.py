"""Match listings: upcoming, live, and completed matches."""

from vlrdevapi._matches.completed import CompletedMatchesNamespace
from vlrdevapi._matches.live import LiveMatchesNamespace
from vlrdevapi._matches.namespace import MatchesNamespace
from vlrdevapi._matches.upcoming import UpcomingMatchesNamespace

__all__ = [
    "CompletedMatchesNamespace",
    "LiveMatchesNamespace",
    "MatchesNamespace",
    "UpcomingMatchesNamespace",
]
