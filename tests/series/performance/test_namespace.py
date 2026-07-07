from unittest.mock import patch

from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
import vlrdevapi

SERIES_ID = 542272
_SERIES_DIR = "series/542272_nrg-vs-fnatic-valorant-champions-2025-gf"
_PERF_FIXTURE = HTMLParser(load_fixture(_SERIES_DIR, "game_233478_performance.html"))
_OVERVIEW = HTMLParser(load_fixture(_SERIES_DIR, "overview.html"))


def _mock_player_mapping(ns, series_id):
    return {"brawk": 2172, "Ethan": 5035, "crashies": 456, "Chronicle": 789}


class TestSyncModuleLevel:
    def test_performance_all(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        assert result.series_id == SERIES_ID
        assert result.game_id == "all"
        assert len(result.all_kills_matrix.entries) == 25
        assert len(result.adv_stats) == 10

    def test_performance_specific_game(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id=233478)
        assert result.series_id == SERIES_ID
        assert result.game_id == "233478"
        assert len(result.all_kills_matrix.entries) == 25
        assert len(result.adv_stats) == 10

    def test_performance_lookup(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        e = result.all_kills_matrix.lookup("brawk", "Chronicle")
        assert e is not None
        assert e.killer == "brawk"
        assert e.killer_team == "NRG"
        assert e.victim == "Chronicle"
        assert e.victim_team == "FNC"
        assert e.kills == 22
        assert e.deaths == 15
        assert e.diff == 7

    def test_performance_by_killer(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        brawk = result.all_kills_matrix.by_killer("brawk")
        assert len(brawk) == 5
        assert all(e.killer == "brawk" for e in brawk)

    def test_performance_by_team(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        nrg = result.all_kills_matrix.by_team("NRG")
        assert len(nrg) == 25

    def test_performance_first_kills_lookup(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        fk = result.first_kills_matrix.lookup("brawk", "Chronicle")
        assert fk is not None
        assert fk.kills == 2
        assert fk.deaths == 1

    def test_performance_adv_stats(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                result = vlrdevapi.series.performance(SERIES_ID, game_id="all")
        brawk = result.adv_stats[0]
        assert brawk.name == "brawk"
        assert brawk.agent == "Sova"
        assert brawk.two_k == 12


class TestSyncWithClient:
    def test_performance_all(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                with vlrdevapi.VLRClient() as client:
                    result = client.series.performance(SERIES_ID, game_id="all")
        assert result.series_id == SERIES_ID
        assert len(result.all_kills_matrix.entries) == 25

    def test_performance_specific_game(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                with vlrdevapi.VLRClient() as client:
                    result = client.series.performance(SERIES_ID, game_id=233478)
        assert result.game_id == "233478"

    def test_curried_match_performance(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                with vlrdevapi.VLRClient() as client:
                    match = client.series(SERIES_ID)
                    result = match.performance(game_id="all")
        assert result.series_id == SERIES_ID
        assert len(result.all_kills_matrix.entries) == 25

    def test_performance_lookup_with_client(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_PERF_FIXTURE):
            with patch("vlrdevapi._series.performance.namespace._get_player_mapping_sync", side_effect=_mock_player_mapping):
                with vlrdevapi.VLRClient() as client:
                    result = client.series.performance(SERIES_ID, game_id="all")
        e = result.all_kills_matrix.lookup("Ethan", "crashies")
        assert e is not None
        assert e.kills == 14
        assert e.deaths == 9
        assert e.diff == 5


