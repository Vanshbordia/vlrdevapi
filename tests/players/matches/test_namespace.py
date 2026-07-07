from datetime import date, timezone
from unittest.mock import patch

from selectolax.parser import HTMLParser

from tests.conftest import load_fixture

_P1 = HTMLParser(load_fixture("player", "11225_ethan", "matches.html"))
_P2 = HTMLParser(load_fixture("player", "11225_ethan", "matches_page2.html"))


def _fetch_side_effect(client, path: str, timeout, retry_config=None, rate_limiter=None) -> HTMLParser:
    if "page=2" in path:
        return _P2
    return _P1


class TestSyncEthan:
    def test_matches_default_limit(self, client):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = client.player.matches(11225)
        assert len(result) == 20
        for m in result:
            assert isinstance(m.match_id, int)
            assert isinstance(m.event, str)
            assert isinstance(m.team1.name, str)
            assert isinstance(m.team2.name, str)

    def test_matches_custom_limit(self, client):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = client.player.matches(11225, limit=3)
        assert len(result) == 3

    def test_matches_static_entry(self, client):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = client.player.matches(11225, limit=100)
        m = next((x for x in result if x.match_id == 684613), None)
        assert m is not None
        assert m.event == "Masters London 2026"
        assert m.bracket == "R1"
        assert m.team1.name == "NRG"
        assert m.team2.name == "Xi Lai Gaming"
        assert m.score1 == 2
        assert m.score2 == 0
        assert m.result == "win"
        assert m.date == date(2026, 6, 6)
        assert m.datetime is not None
        assert m.datetime.tzinfo == timezone.utc

    def test_matches_across_pages(self, client):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = client.player.matches(11225, limit=16)
        assert len(result) == 16
        assert result[0].match_id != result[15].match_id



