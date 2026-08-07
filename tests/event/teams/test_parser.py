from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from vlrdevapi._event.teams.parser import parse_teams


def _fixture() -> HTMLParser:
    return HTMLParser(
        load_fixture("event", "2682_vct-2026-americas-kickoff", "overview.html")
    )


def test_parse_teams_with_players():
    teams = parse_teams(_fixture())

    assert len(teams) > 0

    # Find 100 Thieves and verify its roster parses (name + id only).
    t100 = next(t for t in teams if t.name == "100 Thieves")
    player_names = [p.name for p in t100.players]
    player_ids = [p.id for p in t100.players]

    assert "Asuna" in player_names
    assert "bang" in player_names
    assert 601 in player_ids  # /player/601/asuna
    assert 3880 in player_ids  # /player/3880/bang

    # Every parsed player must have a positive id and non-empty name.
    for team in teams:
        for p in team.players:
            assert p.id > 0
            assert p.name


def test_parse_team_no_players_defaults_empty():
    teams = parse_teams(_fixture())
    # players is always present; even if a team somehow lacks any, it should default to [].
    for team in teams:
        assert isinstance(team.players, list)