from vlrdevapi._client import VLRClient
from vlrdevapi._event.namespace import EventNamespace
from vlrdevapi._matches.namespace import MatchesNamespace
from vlrdevapi._player.namespace import PlayerNamespace
from vlrdevapi._series.namespace import SeriesNamespace
from vlrdevapi._team.namespace import TeamNamespace

__version__: str

team: TeamNamespace
"""Access team data: info, roster, stats, matches, transactions, placements.

Returns:
    TeamNamespace instance bound to the default client. Call with a
    ``team_id`` for curried access, or use the sub-namespace properties
    directly (e.g., ``vlrdevapi.team.info(team_id=4568)``).

Examples:
    >>> info = vlrdevapi.team.info(team_id=4568)
    >>> stats = vlrdevapi.team(4568).stats(last_days=90)
    >>> roster = vlrdevapi.team(4568).roster()
"""

player: PlayerNamespace
"""Access player data: info, teams, agents, match history, and profile.

Returns:
    PlayerNamespace instance bound to the default client.

Examples:
    >>> info = vlrdevapi.player.info(player_id=11225)
    >>> matches = vlrdevapi.player(11225).matches(limit=20)
    >>> agents = vlrdevapi.player(11225).agents(timespan="60d")
"""

series: SeriesNamespace
"""Access series/match data: info, vods, players, rounds, performance, economy.

Returns:
    SeriesNamespace instance bound to the default client.

Examples:
    >>> info = vlrdevapi.series.info(series_id=1)
    >>> players = vlrdevapi.series(1).players(game_id="all")
    >>> rounds = vlrdevapi.series(1).rounds(game_id=1)
"""

event: EventNamespace
"""Access event/tournament data: info, stages, teams, matches, standings, listings.

Returns:
    EventNamespace instance bound to the default client.

Examples:
    >>> info = vlrdevapi.event.info(event_id=123)
    >>> matches = vlrdevapi.event(123).matches(state="upcoming")
    >>> standings = vlrdevapi.event(123).standings(stage="group_a")
"""

matches: MatchesNamespace
"""Access match listings: upcoming, live, and completed matches.

Returns:
    MatchesNamespace instance bound to the default client.

Examples:
    >>> upcoming = vlrdevapi.matches.upcoming()
    >>> live = vlrdevapi.matches.live()
    >>> completed = vlrdevapi.matches.completed()
"""

client: type[VLRClient]
"""Create an explicit VLRClient for connection management.

Returns:
    The ``VLRClient`` class, callable with optional configuration
    arguments (``timeout``, ``max_retries``, etc.) to create a
    new client instance.

Examples:
    >>> client = vlrdevapi.client()
    >>> info = client.series.info(series_id=1)

    >>> with vlrdevapi.client() as c:
    ...     result = c.series.vods(123)
"""
