from unittest.mock import patch

from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi
from vlrdevapi._event.matches.models import MatchStatus


class TestSyncModuleLevel:
    def test_event_matches_vct_emea(self, mock_vlr):
        mock_vlr.get("/event/matches/2863/?series_id=all").respond(
            200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            result = vlrdevapi.event.matches(2863)
        assert result.event_id == 2863
        assert len(result.matches) > 0

    def test_event_matches_completed_filter(self, mock_vlr):
        mock_vlr.get("/event/matches/2863/?series_id=all&group=completed").respond(
            200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_completed.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            result = vlrdevapi.event.matches(2863, state="completed")
        assert result.event_id == 2863
        assert len(result.matches) > 0
        for m in result.matches:
            assert m.status == MatchStatus.COMPLETED

    def test_event_matches_completed_event(self, mock_vlr):
        mock_vlr.get("/event/matches/2760/?series_id=all").respond(
            200, text=load_fixture("event", "2760_valorant-masters-santiago-2026", "matches_all.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            result = vlrdevapi.event.matches(2760, state="all")
        assert result.event_id == 2760
        assert len(result.matches) > 0


class TestSyncWithClient:
    def test_event_matches_curried(self, mock_vlr):
        mock_vlr.get("/event/matches/2863/?series_id=all").respond(
            200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            with vlrdevapi.VLRClient() as client:
                result = client.event(2863).matches()
        assert result.event_id == 2863
        assert len(result.matches) > 0

    def test_event_matches_direct(self, mock_vlr):
        mock_vlr.get("/event/matches/2863/?series_id=all").respond(
            200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_all.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            with vlrdevapi.VLRClient() as client:
                result = client.event.matches(2863)
        assert result.event_id == 2863
        assert len(result.matches) > 0

    def test_event_matches_with_state(self, mock_vlr):
        mock_vlr.get("/event/matches/2863/?series_id=all&group=completed").respond(
            200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "matches_completed.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            with vlrdevapi.VLRClient() as client:
                result = client.event.matches(2863, state="completed")
        assert len(result.matches) > 0

    def test_event_matches_completed_event(self, mock_vlr):
        mock_vlr.get("/event/matches/2760/?series_id=all").respond(
            200, text=load_fixture("event", "2760_valorant-masters-santiago-2026", "matches_all.html")
        )

        with patch("vlrdevapi._event.matches.namespace._enrich_match_teams"):
            with vlrdevapi.VLRClient() as client:
                result = client.event.matches(2760)
        assert result.event_id == 2760
        assert len(result.matches) > 0



