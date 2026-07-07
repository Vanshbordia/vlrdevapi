from unittest.mock import patch

from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
import vlrdevapi

SERIES_ID = 542272
_SERIES_DIR = "series/542272_nrg-vs-fnatic-valorant-champions-2025-gf"
_OVERVIEW = HTMLParser(load_fixture(_SERIES_DIR, "overview.html"))
_GAME_OVERVIEW = HTMLParser(load_fixture(_SERIES_DIR, "game_233478_overview.html"))


def _fetch_side_effect(client, path: str, timeout, retry_config=None, rate_limiter=None) -> HTMLParser:
    if "game=233478" in path:
        return _GAME_OVERVIEW
    return _OVERVIEW


class TestSyncModuleLevel:
    def test_players_all(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = vlrdevapi.series.players(SERIES_ID, game_id="all")
        assert result.series_id == SERIES_ID
        assert result.game_id == "all"
        assert result.team1.team_id == 1034
        assert result.team1.team_name == "NRG"
        assert result.team2.team_id == 2593
        assert result.team2.team_name == "FNATIC"
        assert len(result.team1.players) == 5
        assert len(result.team2.players) == 5

    def test_players_specific_game(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = vlrdevapi.series.players(SERIES_ID, game_id=233478)
        assert result.series_id == SERIES_ID
        assert result.game_id == "233478"
        assert result.map_name == "Corrode"
        assert len(result.team1.players) == 5
        assert len(result.team2.players) == 5

    def test_brawk_all_stats(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            result = vlrdevapi.series.players(SERIES_ID, game_id="all")
        brawk = result.team1.players[0]
        assert brawk.player_id == 2172
        assert brawk.name == "brawk"
        assert brawk.agents == ["Sova", "Vyse"]
        assert brawk.stats.overall.rating == 1.27


class TestSyncWithClient:
    def test_players_all(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            with vlrdevapi.VLRClient() as client:
                result = client.series.players(SERIES_ID, game_id="all")
        assert result.series_id == SERIES_ID
        assert result.team1.team_id == 1034
        assert result.team2.team_id == 2593

    def test_players_specific_game(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            with vlrdevapi.VLRClient() as client:
                result = client.series.players(SERIES_ID, game_id=233478)
        assert result.map_name == "Corrode"
        brawk = result.team1.players[0]
        assert brawk.stats.overall.rating == 1.93

    def test_curried_match_players(self):
        with patch("vlrdevapi._base.fetch_sync", side_effect=_fetch_side_effect):
            with vlrdevapi.VLRClient() as client:
                match = client.series(SERIES_ID)
                result = match.players(game_id="all")
        assert result.series_id == SERIES_ID
        assert result.game_id == "all"



