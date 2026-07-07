from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi
from vlrdevapi._event.stages.models import EventStages


class TestSyncModuleLevel:
    def test_event_stages_vct_emea(self, mock_vlr):
        mock_vlr.get("/event/matches/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html"))
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        result = vlrdevapi.event.stages(2863)
        assert result is not None
        assert isinstance(result, EventStages)
        assert len(result.stages) >= 1

    def test_event_stages_curried(self, mock_vlr):
        mock_vlr.get("/event/matches/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html"))
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.event(2863).stages()
        assert result is not None
        assert len(result.stages) >= 1

    def test_event_stages_direct(self, mock_vlr):
        mock_vlr.get("/event/matches/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html"))
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.event.stages(2863)
        assert result is not None
        assert len(result.stages) >= 1


class TestEventWithoutStages:
    def test_event_without_stages_returns_empty(self, mock_vlr):
        mock_vlr.get("/event/matches/2949").respond(200, text=load_fixture("event", "2949_gameon-productivity-and-technology-tournament-2026", "overview.html"))
        mock_vlr.get("/event/2949").respond(200, text=load_fixture("event", "2949_gameon-productivity-and-technology-tournament-2026", "overview.html"))

        result = vlrdevapi.event.stages(2949)
        assert isinstance(result, EventStages)

