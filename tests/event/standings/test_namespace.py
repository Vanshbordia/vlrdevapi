from unittest.mock import patch

import pytest
from selectolax.parser import HTMLParser

from tests.conftest import _LIVE, live_fetch, load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi
from vlrdevapi.exceptions import NotFoundError


def _load_overview(event_id: int, slug: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/event/{event_id}"))
    return HTMLParser(load_fixture("event", f"{event_id}_{slug}", "overview.html"))


class TestEventStandingsNamespace:
    def test_get_standings_sync(self, mock_vlr):
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        # Patch _parallel_fetch to return the same overview HTML for all stage fetches
        overview_html = _load_overview(2863, "vct-2026-emea-stage-1")

        with patch("vlrdevapi._event.standings.namespace.SyncNamespace._parallel_fetch") as mock_pf:
            mock_pf.return_value = [overview_html]

            standings = vlrdevapi.event.standings(2863)
        assert len(standings) > 0
        for stage in standings:
            assert stage.stage_name != ""
            assert isinstance(stage.standings, list)
            for entry in stage.standings:
                assert entry.place != ""
                assert entry.team is not None
                assert entry.team.name != ""

    def test_get_standings_with_client(self, mock_vlr):
        mock_vlr.get("/event/2863").respond(200, text=load_fixture("event", "2863_vct-2026-emea-stage-1", "overview.html"))

        overview_html = _load_overview(2863, "vct-2026-emea-stage-1")

        with patch("vlrdevapi._event.standings.namespace.SyncNamespace._parallel_fetch") as mock_pf:
            mock_pf.return_value = [overview_html]

            with vlrdevapi.VLRClient() as client:
                standings = client.event(2863).standings()
        assert len(standings) > 0
        for stage in standings:
            assert stage.stage_name != ""
            assert isinstance(stage.standings, list)

    def test_get_standings_non_existent(self, mock_vlr):
        mock_vlr.get("/event/999999").respond(404)

        with pytest.raises(NotFoundError):
            vlrdevapi.event.standings(999999)

    def test_get_standings_curried_sync(self, mock_vlr):
        mock_vlr.get("/event/2682").respond(200, text=load_fixture("event", "2682_vct-2026-americas-kickoff", "overview.html"))

        overview_html = _load_overview(2682, "vct-2026-americas-kickoff")

        with patch("vlrdevapi._event.standings.namespace.SyncNamespace._parallel_fetch") as mock_pf:
            mock_pf.return_value = [overview_html]

            with vlrdevapi.VLRClient() as client:
                standings = client.event(2682).standings()
        assert len(standings) > 0
        assert any(s.stage_name != "" for s in standings)

