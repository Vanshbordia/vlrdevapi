from unittest.mock import patch
import pytest
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
import vlrdevapi
from vlrdevapi.exceptions import ValidationError

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str = "completed_matches.html") -> HTMLParser:
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


def _fake_fetch(pages: dict[int, HTMLParser]):
    def _fetch(client, path, *args, **kwargs):
        if "page=" in path:
            page = int(path.rsplit("page=", 1)[1].split("&")[0])
        else:
            page = 1
        parser = pages.get(page)
        return parser if parser is not None else HTMLParser("<html></html>")
    return _fetch


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


class TestPagination:
    def _result(self, pages, **kwargs):
        with (
            patch("vlrdevapi._base.fetch_sync") as mock_fetch,
            patch(
                "vlrdevapi._team.completed_matches.namespace.enrich_team_match_sync"
            ),
        ):
            mock_fetch.side_effect = _fake_fetch(pages)
            result = vlrdevapi.team.completed_matches(120, **kwargs)
        return result, mock_fetch

    def test_default_returns_first_page_only(self):
        result, mock_fetch = self._result({1: _load_page(120, 1)})

        assert len(result.matches) == 50
        assert result.has_next_page is True
        assert mock_fetch.call_count == 1

    def test_limit_smaller_than_page_size(self):
        result, mock_fetch = self._result({1: _load_page(120, 1)}, limit=10)

        assert len(result.matches) == 10
        assert mock_fetch.call_count == 1

    def test_limit_80_fetches_two_pages(self):
        pages = {1: _load_page(120, 1), 2: _load_page(120, 2)}
        result, mock_fetch = self._result(pages, limit=80)

        assert len(result.matches) == 80
        assert result.matches[49].match_id == 530909
        assert result.matches[50].match_id == 530905
        assert result.matches[-1].match_id == 371267
        assert result.has_next_page is True
        assert mock_fetch.call_count == 2

    def test_return_all_fetches_every_page(self):
        pages = {1: _load_page(120, 1), 2: _load_page(120, 2)}
        result, mock_fetch = self._result(pages, limit=10, return_all=True)

        assert len(result.matches) == 100
        assert result.has_next_page is False
        assert mock_fetch.call_count == 3

    def test_curried_accepts_limit(self):
        with (
            patch("vlrdevapi._base.fetch_sync") as mock_fetch,
            patch(
                "vlrdevapi._team.completed_matches.namespace.enrich_team_match_sync"
            ),
        ):
            mock_fetch.side_effect = _fake_fetch({1: _load_page(120, 1)})
            result = vlrdevapi.team(120).completed_matches(limit=10)

        assert len(result.matches) == 10
        assert mock_fetch.call_count == 1

    def test_invalid_limit(self):
        with pytest.raises(ValidationError):
            vlrdevapi.team.completed_matches(120, limit=0)
