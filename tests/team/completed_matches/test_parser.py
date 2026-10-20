import pytest
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._team.completed_matches.parser import (
    _parse_match_item,
    parse_team_completed_matches,
)
from vlrdevapi._team.completed_matches.models import TeamCompletedMatches

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/team/{team_id}"))
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


def _load_page(team_id: int, page: int) -> HTMLParser:
    if _LIVE:
        path = f"/team/matches/{team_id}/?core_id=all&group=completed"
        if page > 1:
            path += f"&page={page}"
        return HTMLParser(live_fetch(path))
    filename = "completed_matches.html" if page == 1 else f"completed_matches_page{page}.html"
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseMatchItem:
    def test_parse_match_item_basic(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        assert len(items) > 0

        match = _parse_match_item(items[0], 1034)
        assert match is not None
        assert match.match_id > 0
        assert match.url.startswith("https://www.vlr.gg/")

    def test_parse_match_item_scores(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        match = _parse_match_item(items[0], 1034)

        assert match is not None
        assert match.team_score >= 0
        assert match.opponent_score >= 0
        assert isinstance(match.is_win, bool)

    def test_parse_match_item_datetime(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        match = _parse_match_item(items[0], 1034)

        assert match is not None
        if match.datetime is not None:
            assert match.datetime.year >= 2020

    def test_parse_all_match_items(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        for item in items:
            match = _parse_match_item(item, 1034)
            if match:
                assert match.match_id > 0
                assert match.url.startswith("https://")


class TestParseTeamCompletedMatches:
    def test_parse_without_enrichment(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")

        result = TeamCompletedMatches(team_id=1034)
        for item in items:
            match = _parse_match_item(item, 1034)
            if match and match.match_id > 0:
                result.matches.append(match)

        assert result.team_id == 1034
        assert len(result.matches) > 0

        for m in result.matches:
            assert m.match_id > 0
            assert m.url.startswith("https://")


class TestParseTeamCompletedMatchesPagination:
    def test_first_page_has_next(self):
        result = parse_team_completed_matches(_load_page(120, 1), 120)
        assert len(result.matches) == 50
        assert result.has_next_page is True

    def test_second_page(self):
        result = parse_team_completed_matches(_load_page(120, 2), 120)
        assert len(result.matches) == 50
        assert result.has_next_page is True
        assert result.matches[0].match_id == 530905

    def test_last_page_has_no_next(self):
        result = parse_team_completed_matches(_load_page(17676, 1), 17676)
        # Humble 5's completed history fits on a single page.
        assert result.matches
        assert result.has_next_page is False

