from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi

SERIES_ID = 542272
_SERIES_DIR = "542272_nrg-vs-fnatic-valorant-champions-2025-gf"


class TestSyncModuleLevel:
    def test_series_info(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.info(SERIES_ID)
        assert result.series_id == SERIES_ID
        assert result.status == "completed"
        assert result.event_name == "Valorant Champions 2025"
        assert result.stage == "Playoffs"
        assert result.bracket == "Grand Final"
        assert result.team1.name == "NRG"
        assert result.team1.tag == "NRG"
        assert result.team2.name == "FNATIC"
        assert result.team2.tag == "FNC"
        assert result.score1 == 3
        assert result.score2 == 2
        assert result.best_of == 5
        assert result.patch == "11.05"
        assert len(result.veto) == 7
        assert result.datetime is not None
        assert len(result.games) == 5
        assert result.games[0].game_id == 233478
        assert result.games[0].order == 1
        assert result.games[0].map_name == "Corrode"
        assert result.games[0].picked_by == "NRG"
        assert result.games[0].played is True
        assert result.games[4].game_id == 233482
        assert result.games[4].order == 5
        assert result.games[4].map_name == "Sunset"


class TestSyncWithClient:
    def test_series_info(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.series.info(SERIES_ID)
        assert result.series_id == SERIES_ID
        assert result.status == "completed"
        assert result.team1.id == 1034
        assert result.team2.id == 2593
        assert result.score1 == 3
        assert result.score2 == 2

