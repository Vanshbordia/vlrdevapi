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
        assert result.vods[0].label == "Full match"
        assert "twitch.tv" in result.vods[0].url
        assert result.vods[1].label == "Corrode"
        assert "youtu" in result.vods[1].url

    def test_vods_labels(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        labels = [v.label for v in result.vods]
        assert "Full match" in labels
        assert "Corrode" in labels
        assert "Lotus" in labels

    def test_vods_urls_have_domain(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        for vod in result.vods:
            assert vod.url.startswith("http")

    def test_streams_are_parsed(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        assert len(result.streams) == 38

        first = result.streams[0]
        assert first.platform == "twitch"
        assert first.channel == "Valorant"
        assert first.url == "https://www.twitch.tv/valorant"
        assert first.stream_type == "broadcast"
        assert first.country_code == "un"

    def test_vod_metadata(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        result = vlrdevapi.series.vods(SERIES_ID)
        full_match = result.vods[0]
        assert full_match.label == "Full match"
        assert full_match.platform == "twitch"
        assert full_match.map_number is None
        assert full_match.start_seconds == 8057

        first_map = result.vods[1]
        assert first_map.label == "Corrode"
        assert first_map.platform == "youtube"
        assert first_map.map_number == 1
        assert first_map.start_seconds == 132

    def test_upcoming_series_streams_without_vods(self, mock_vlr):
        mock_vlr.get("/777944").respond(
            200, text=load_fixture("series", "777944", "overview.html"),
        )

        result = vlrdevapi.series.vods(777944)
        assert len(result.streams) == 7
        assert result.vods == []

        platforms = {stream.platform for stream in result.streams}
        assert {"twitch", "youtube", "bilibili", "douyu", "huya"} <= platforms

    def test_watch_parties_are_kept_separate_from_broadcasts(self, mock_vlr):
        mock_vlr.get("/754737").respond(
            200,
            text=load_fixture(
                "series",
                "754737_loud-vs-team-vitality-valorant-champions-2026-gf",
                "overview.html",
            ),
        )

        result = vlrdevapi.series.vods(754737)
        assert any(stream.stream_type == "broadcast" for stream in result.streams)
        assert any(stream.stream_type == "watchparty" for stream in result.streams)
        assert any(stream.platform == "kick" for stream in result.streams)


class TestSyncWithClient:
    def test_series_vods(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", _SERIES_DIR, "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.series.vods(SERIES_ID)
        assert result.series_id == SERIES_ID
        assert result.vods[0].label == "Full match"
        assert "twitch.tv" in result.vods[0].url

