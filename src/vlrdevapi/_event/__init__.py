"""Event/tournament data: info, stages, teams, matches, standings, listings."""

from vlrdevapi._event.list.namespace import EventListNamespace
from vlrdevapi._event.matches.namespace import EventMatchesNamespace
from vlrdevapi._event.namespace import EventNamespace
from vlrdevapi._event.stages.namespace import EventStagesNamespace
from vlrdevapi._event.standings.namespace import EventStandingsNamespace
from vlrdevapi._event.teams.namespace import EventTeamsNamespace

__all__ = [
    "EventListNamespace",
    "EventMatchesNamespace",
    "EventNamespace",
    "EventStagesNamespace",
    "EventStandingsNamespace",
    "EventTeamsNamespace",
]
