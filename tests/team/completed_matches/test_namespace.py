from unittest.mock import patch
import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
import vlrdevapi

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str = "completed_matches.html") -> HTMLParser:
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestSyncModuleLevel:
    def test_team_completed_matches_nrg(self):
        html = _load_html(1034)
        with patch("vlrdevapi._base.fetch_sync") as mock_fetch:
            mock_fetch.return_value = html
            result = vlrdevapi.team.completed_matches(1034)
        assert result.team_id == 1034
        assert len(result.matches) > 0

        match = result.matches[0]
        assert match.match_id > 0
        assert match.url.startswith("https://www.vlr.gg/")
        assert isinstance(match.is_win, bool)

    def test_team_completed_matches_curried(self):
        html = _load_html(1034)
        with patch("vlrdevapi._base.fetch_sync") as mock_fetch:
            mock_fetch.return_value = html
            result = vlrdevapi.team(1034).completed_matches()
        assert result.team_id == 1034
        assert len(result.matches) > 0


class TestSyncWithClient:
    def test_team_completed_matches_direct(self):
        html = _load_html(1034)
        with patch("vlrdevapi._base.fetch_sync") as mock_fetch:
            mock_fetch.return_value = html
            with vlrdevapi.VLRClient() as client:
                result = client.team.completed_matches(1034)
        assert result.team_id == 1034
        assert len(result.matches) > 0

    def test_team_completed_matches_curried_client(self):
        html = _load_html(1034)
        with patch("vlrdevapi._base.fetch_sync") as mock_fetch:
            mock_fetch.return_value = html
            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).completed_matches()
        assert result.team_id == 1034
        assert len(result.matches) > 0




class TestWithFixture:
    def test_from_fixture_basic(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")
        assert len(items) > 0

    def test_from_fixture_match_data(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")

        for item in items[:3]:
            href = item.attributes.get("href") or ""
            assert href.startswith("/")

            result_el = item.css_first(".m-item-result")
            if result_el:
                spans = result_el.css("span")
                if len(spans) >= 2:
                    score1 = spans[0].text(strip=True)
                    score2 = spans[-1].text(strip=True)
                    assert score1.isdigit()
                    assert score2.isdigit()

    def test_from_fixture_event_data(self):
        html = _load_html(1034, "completed_matches.html")
        items = html.css("a.wf-card.fc-flex.m-item")

        for item in items[:3]:
            event_el = item.css_first(".m-item-event")
            if event_el:
                divs = event_el.css("div")
                if len(divs) >= 2:
                    event_name = divs[1].text(strip=True)
                    assert event_name
