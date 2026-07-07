import logging
from collections.abc import Callable
from typing import Protocol, TypeVar

from selectolax.parser import HTMLParser

from vlrdevapi._cache import LRUCache
from vlrdevapi._utils.paths import team as team_path
from vlrdevapi._utils.team_parsing import _parse_team_basic
from vlrdevapi.exceptions import VlrdevapiException

logger = logging.getLogger(__name__)


class SeriesTeamProtocol(Protocol):
    id: int


class SeriesInfoProtocol(Protocol):
    team1: SeriesTeamProtocol | None
    team2: SeriesTeamProtocol | None
    event_name: str
    stage: str
    bracket: str


class OpponentProtocol(Protocol):
    def __init__(self, *, id: int = 0, name: str = "", tag: str = "") -> None: ...  # noqa: A002
    name: str
    tag: str


OpponentT = TypeVar("OpponentT", bound=OpponentProtocol)


def enrich_team_match_sync(
    match,
    team_id: int,
    series_info_fn: Callable[[int], SeriesInfoProtocol],
    fetch_fn: Callable[[str], HTMLParser],
    team_cache: LRUCache[int, dict[str, str]],
    opponent_cls: type[OpponentT],
    log_label: str,
) -> None:
    try:
        series_info = series_info_fn(match.match_id)
        team1_id = series_info.team1.id if series_info.team1 else 0
        team2_id = series_info.team2.id if series_info.team2 else 0
        opponent_id = team2_id if team1_id == team_id else team1_id

        if series_info.event_name:
            match.event = series_info.event_name
        if series_info.stage:
            match.stage = series_info.stage
        if series_info.bracket:
            match.stage = f"{match.stage} - {series_info.bracket}".strip(" -")

        if opponent_id > 0:
            opponent = opponent_cls(id=opponent_id)
            cached = team_cache.get(opponent_id)
            if cached is not None:
                opponent.name = cached["name"]
                opponent.tag = cached["tag"]
            else:
                try:
                    url = team_path(opponent_id)
                    info = _parse_team_basic(fetch_fn(url))
                    opponent.name = info["name"]
                    opponent.tag = info["tag"]
                    team_cache.put(opponent_id, info)
                except (VlrdevapiException, KeyError):
                    logger.warning("Failed to fetch team info for team %d", opponent_id)
                    raise
            match.opponent = opponent
    except (VlrdevapiException, AttributeError, KeyError, TypeError, ValueError):
        logger.warning("Failed to enrich %s match %d", log_label, match.match_id)
        raise



