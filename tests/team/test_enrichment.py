from selectolax.lexbor import LexborHTMLParser as HTMLParser

from vlrdevapi._cache import LRUCache
from vlrdevapi._team.completed_matches.models import (
    OpponentInCompletedMatch,
    TeamCompletedMatchEntry,
)
from vlrdevapi._utils.team_enrichment import enrich_team_match_sync


class _Team:
    id = 0


class _SeriesInfo:
    team1 = _Team()
    team2 = _Team()
    event_name = "Champions 2026"
    stage = "Playoffs"
    bracket = "LBF"


def test_enrichment_sets_stage_and_bracket_separately():
    match = TeamCompletedMatchEntry(match_id=123, stage="Week 1", bracket="Ro12")
    calls: list[str] = []

    def fetch_fn(url: str) -> HTMLParser:  # pragma: no cover - must not be called
        calls.append(url)
        raise AssertionError("team fetch should not happen when both team IDs are 0")

    enrich_team_match_sync(
        match,
        120,
        lambda _match_id: _SeriesInfo(),
        fetch_fn,
        LRUCache(),
        OpponentInCompletedMatch,
        "completed",
    )

    assert match.event == "Champions 2026"
    assert match.stage == "Playoffs"
    assert match.bracket == "LBF"
    assert match.stage != "Playoffs - LBF"
    assert calls == []
