from unittest.mock import patch

from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
import vlrdevapi

_EVENT_FIXTURE = HTMLParser(load_fixture("event", "2682_vct-2026-americas-kickoff", "overview.html"))


def test_teams_filtering():
    event_id = 2682

    with patch("vlrdevapi._base.fetch_sync", return_value=_EVENT_FIXTURE):
        with patch("vlrdevapi._base.SyncNamespace._parallel_fetch", return_value=[_EVENT_FIXTURE]):
            all_stages = vlrdevapi.event.teams(event_id)
    assert len(all_stages) >= 1

    with patch("vlrdevapi._base.fetch_sync", return_value=_EVENT_FIXTURE):
        with patch("vlrdevapi._base.SyncNamespace._parallel_fetch", return_value=[_EVENT_FIXTURE]):
            main_event = vlrdevapi.event.teams(event_id, stage="main-event")
    assert len(main_event) == 1
    assert "main-event" in main_event[0].stage_path.lower() or "main" in main_event[0].stage_name.lower()


def test_teams_no_subnav():
    event_id = 2682

    with patch("vlrdevapi._base.fetch_sync", return_value=_EVENT_FIXTURE):
        with patch("vlrdevapi._base.SyncNamespace._parallel_fetch", return_value=[_EVENT_FIXTURE]):
            teams = vlrdevapi.event.teams(event_id)
    assert len(teams) > 0
