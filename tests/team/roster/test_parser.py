import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._team.roster.parser import parse_team_roster


def _load_html(team_id: int) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/team/{team_id}"))
    path = (
        FIXTURES_DIR
        / "team"
        / str(team_id)
        / "overview_light.html"
    )
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseTeamRoster:
    def test_parse_100_thieves_roster(self):
        html = _load_html(120)
        roster = parse_team_roster(html)

        assert len(roster.players) > 0
        assert len(roster.staff) > 0

        # Check a player
        player = roster.players[0]
        assert player.id > 0
        assert player.ign
        assert player.real_name
        assert player.country
        assert player.roles
        assert player.photo_url.startswith("https://")

    def test_parse_team_without_roster(self):
        # Assuming team 17676 has no roster
        from vlrdevapi.exceptions import DataNotFoundError
        html = _load_html(17676)
        with pytest.raises(DataNotFoundError, match="roster not found on team page"):
            parse_team_roster(html)

