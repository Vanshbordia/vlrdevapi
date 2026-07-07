"""vlrdevapi — A Python library to scrape data from vlr.gg.

Provides a synchronous, typed interface for accessing match listings,
event data, tournament info, team/player profiles, and statistics
from vlr.gg.

Examples:
    Module-level access (using a default client):

    >>> import vlrdevapi
    >>> info = vlrdevapi.team.info(team_id=4568)
    >>> info.name
    'Sentinels'

    Explicit client with context manager:

    >>> with vlrdevapi.VLRClient() as client:
    ...     result = client.series.vods(123)

    Curried access (pre-bound ID):

    >>> matches = vlrdevapi.team(4568).completed_matches()
    >>> matches.matches[0].score
    '2-1'

"""

import atexit as _atexit
from typing import TYPE_CHECKING

from vlrdevapi._client import VLRClient
import contextlib

if TYPE_CHECKING:
    from vlrdevapi._event.namespace import EventNamespace
    from vlrdevapi._matches.namespace import MatchesNamespace
    from vlrdevapi._player.namespace import PlayerNamespace
    from vlrdevapi._series.namespace import SeriesNamespace
    from vlrdevapi._team.namespace import TeamNamespace

    event: EventNamespace
    series: SeriesNamespace
    player: PlayerNamespace
    team: TeamNamespace
    matches: MatchesNamespace
    client: type[VLRClient]

__version__ = "2.0.0"

_default_client: "VLRClient | None" = None


def _get_default_client() -> "VLRClient":
    global _default_client  # noqa: PLW0603
    if _default_client is None:
        _default_client = VLRClient()
    return _default_client


def _cleanup_default_client() -> None:
    global _default_client  # noqa: PLW0603
    if _default_client is not None:
        with contextlib.suppress(OSError):
            _default_client.close()
        _default_client = None


_atexit.register(_cleanup_default_client)

_BOUND_NAMES = frozenset({"event", "series", "player", "team", "matches"})


def __getattr__(name: str) -> object:
    if name in _BOUND_NAMES:
        return getattr(_get_default_client(), name)
    if name == "client":
        return VLRClient
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def __dir__() -> list[str]:
    return sorted(__all__)


__all__ = [
    "VLRClient",
    "__version__",
    "client",
    "event",
    "matches",
    "player",
    "series",
    "team",
]
