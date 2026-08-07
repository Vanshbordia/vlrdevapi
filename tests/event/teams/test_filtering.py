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


def test_teams_include_players():
    event_id = 2682

    with patch("vlrdevapi._base.fetch_sync", return_value=_EVENT_FIXTURE):
        with patch("vlrdevapi._base.SyncNamespace._parallel_fetch", return_value=[_EVENT_FIXTURE]):
            teams = vlrdevapi.event.teams(event_id)

    # Flatten teams across stages and confirm at least one team has players.
    all_teams = [team for stage in teams for team in stage.teams]
    assert all_teams

    any_with_players = [team for team in all_teams if team.players]
    assert any_with_players

    # Verify a specific known player (Asuna, id 601) is present.
    player_refs = {
        (p.id, p.name) for team in any_with_players for p in team.players
    }
    assert (601, "Asuna") in player_refs
