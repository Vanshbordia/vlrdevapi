from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi


class TestSyncModuleLevel:
    def test_event_info_vct_emea(self, mock_vlr):
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        result = vlrdevapi.event.info(2863)
        assert result.id == 2863
        assert result.name == "VCT 2026: EMEA Stage 1"
        assert result.subtitle != ""
        assert result.image_url.startswith("https://")
        assert result.series is not None
        assert result.series.name == "Valorant Champions Tour 2026"
        assert result.stage is not None
        assert result.stage.name == "Stage 1"
        assert len(result.regions) >= 1
        assert any(r.name == "EMEA" for r in result.regions)
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.prize is not None
        assert result.prize.is_tbd is True
        assert result.location is not None
        assert result.location.country == "Germany"

    def test_event_info_gameon(self, mock_vlr):
        mock_vlr.get("/event/2949").respond(200, text=load_fixture("event", "2949_gameon-productivity-and-technology-tournament-2026", "overview.html"))

        result = vlrdevapi.event.info(2949)
        assert result.id == 2949
        assert result.name == "GAMEON Productivity and Technology Tournament 2026"
        assert result.series is None
        assert result.prize is not None
        assert result.prize.amount == 600000
        assert result.prize.converted_amount == 13403

    def test_event_info_challengers_japan(self, mock_vlr):
        mock_vlr.get("/event/2847").respond(200, text=load_fixture("event", "2847_challengers-2026-japan-split-1", "overview.html"))

        result = vlrdevapi.event.info(2847)
        assert result.id == 2847
        assert result.name == "Challengers 2026: Japan Split 1"
        assert result.prize is not None
        assert result.prize.amount == 4000000
        assert result.prize.currency_code == "JPY"
        assert result.prize.converted_amount == 25656
        assert result.region_location is not None
        assert result.region_location.country == "Japan"

    def test_event_info_single_day(self, mock_vlr):
        mock_vlr.get("/event/58").respond(200, text=load_fixture("event", "58_100t-x-cashapp-gamers-for-equality", "overview.html"))

        result = vlrdevapi.event.info(58)
        assert result.id == 58
        assert result.name == "100T x Cashapp Gamers for Equality"
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.start_date == result.end_date
        assert result.prize is not None
        assert result.prize.amount == 0

    def test_event_info_vct_americas(self, mock_vlr):
        mock_vlr.get("/event/2682").respond(200, text=load_fixture("event", "2682_vct-2026-americas-kickoff", "overview.html"))

        result = vlrdevapi.event.info(2682)
        assert result.id == 2682
        assert result.name == "VCT 2026: Americas Kickoff"
        assert result.series is not None
        assert result.stage is not None
        assert len(result.regions) >= 1
        assert result.location is not None
        assert "Los Angeles" in result.location.venue


class TestSyncWithClient:
    def test_event_info_curried(self, mock_vlr):
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.event(2863).info()
        assert result.id == 2863
        assert result.name == "VCT 2026: EMEA Stage 1"

    def test_event_info_direct(self, mock_vlr):
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.event.info(2863)
        assert result.id == 2863
        assert result.name == "VCT 2026: EMEA Stage 1"

