from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi

SERIES_ID = 542272
_SERIES_DIR = "542272_nrg-vs-fnatic-valorant-champions-2025-gf"


class TestSyncModuleLevel:
    def test_series_vods(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        assert result.series_id == SERIES_ID
        assert len(result.vods) > 0
        assert result.vods[0].label == "Full Match"
        assert "twitch.tv" in result.vods[0].url
        assert result.vods[1].label == "Map 1"
        assert "youtu" in result.vods[1].url

    def test_vods_labels(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        labels = [v.label for v in result.vods]
        assert "Full Match" in labels
        assert "Map 1" in labels
        assert "Map 2" in labels

    def test_vods_urls_have_domain(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        for vod in result.vods:
            assert vod.url.startswith("http")


class TestSyncWithClient:
    def test_series_vods(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.series.vods(SERIES_ID)
        assert result.series_id == SERIES_ID
        assert result.vods[0].label == "Full Match"
        assert "twitch.tv" in result.vods[0].url

