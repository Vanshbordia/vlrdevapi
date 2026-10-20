from datetime import UTC, datetime

import pytest
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import _LIVE, FIXTURES_DIR, live_fetch
from vlrdevapi._team.upcoming_matches.parser import (
    _parse_match_item,
    parse_team_upcoming_matches,
)

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str = "overview_light.html") -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/team/{team_id}"))
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseMatchItem:
    def test_parse_match_item_from_completed(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        assert len(items) > 0

        for item in items[:3]:
            match = _parse_match_item(item)
            assert match is not None
            assert match.match_id > 0
            assert match.url.startswith("https://www.vlr.gg/")
            assert match.event
            assert isinstance(match.stage, str)

    def test_parse_match_item_datetime(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        assert len(items) > 0

        match = _parse_match_item(items[0])
        assert match is not None
        if match.datetime is not None:
            assert isinstance(match.datetime, datetime)
            assert match.datetime.tzinfo == UTC

    def test_parse_all_match_items(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")

        for item in items:
            match = _parse_match_item(item)
            if match:
                assert match.match_id > 0
                assert match.url.startswith("https://")


class TestParseTeamUpcomingMatches:
    def test_parse_without_enrichment(self):
        html = _load_html(1034)
        result = parse_team_upcoming_matches(html, 1034)
        assert result.team_id == 1034
        assert isinstance(result.matches, list)
        for m in result.matches:
            assert m.match_id > 0
            assert m.url.startswith("https://")

    def test_parse_team_with_no_upcoming_matches(self):
        html = _load_html(17676)
        result = parse_team_upcoming_matches(html, 17676)
        assert result.team_id == 17676
        assert len(result.matches) == 0

    def test_parse_multiple_teams(self):
        for team_id in [1034, 120, 2]:
            html = _load_html(team_id)
            result = parse_team_upcoming_matches(html, team_id)
            assert result.team_id == team_id
            assert isinstance(result.matches, list)
            for m in result.matches:
                assert m.match_id > 0
                assert m.url.startswith("https://")

    def test_stage_and_bracket_are_parsed_separately(self):
        html = _load_html(13790)
        result = parse_team_upcoming_matches(html, 13790)

        assert len(result.matches) == 1
        match = result.matches[0]
        assert match.event == "VCT CN 26: Threshold"
        assert match.stage == "Week 1"
        assert match.bracket == "Ro12"

    def test_parse_only_upcoming_section(self):
        """Regression: the section after the heading must not include Recent Results."""
        html = _load_html(13790)
        result = parse_team_upcoming_matches(html, 13790)

        assert [m.match_id for m in result.matches] == [777944]
        # The page contains five recent results (748620, 724627, 724625, ...).
        assert all(m.match_id != 748620 for m in result.matches)

