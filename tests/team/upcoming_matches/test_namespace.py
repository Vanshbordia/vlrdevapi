from unittest.mock import patch
import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
import vlrdevapi

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str = "overview_light.html") -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/team/{team_id}"))
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestSyncModuleLevel:
    def test_team_upcoming_matches_nrg_with_fixture(self):
        html = _load_html(1034)
        with patch(
            "vlrdevapi._base.fetch_sync"
        ) as mock_fetch:
            mock_fetch.return_value = html

            result = vlrdevapi.team.upcoming_matches(1034)
            assert result.team_id == 1034
            assert isinstance(result.matches, list)

            if result.matches:
                match = result.matches[0]
                assert match.match_id > 0
                assert match.url.startswith("https://www.vlr.gg/")

    def test_team_upcoming_matches_curried_with_fixture(self):
        html = _load_html(1034)
        with patch(
            "vlrdevapi._base.fetch_sync"
        ) as mock_fetch:
            mock_fetch.return_value = html

            result = vlrdevapi.team(1034).upcoming_matches()
            assert result.team_id == 1034


class TestSyncWithClient:
    def test_team_upcoming_matches_direct_with_fixture(self):
        html = _load_html(1034)
        with patch(
            "vlrdevapi._base.fetch_sync"
        ) as mock_fetch:
            mock_fetch.return_value = html

            with vlrdevapi.VLRClient() as client:
                result = client.team.upcoming_matches(1034)
            assert result.team_id == 1034

    def test_team_upcoming_matches_curried_client_with_fixture(self):
        html = _load_html(1034)
        with patch(
            "vlrdevapi._base.fetch_sync"
        ) as mock_fetch:
            mock_fetch.return_value = html

            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).upcoming_matches()
            assert result.team_id == 1034


