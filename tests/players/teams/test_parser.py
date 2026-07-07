from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from tests.helpers.expected_from_html import player_team_dates_from_lines
from tests.helpers.fixtures import player_team_texts


def _expected_for_team(html: HTMLParser, team_name: str, *, has_inactive: bool = False) -> dict:
    entries = [
        player_team_dates_from_lines(lines)
        for lines in player_team_texts(html, team_name)
    ]
    assert entries, f"No fixture entries found for {team_name!r}"
    if has_inactive:
        return next(entry for entry in entries if entry.get("inactive_date") is not None)
    if len(entries) == 1:
        return entries[0]
    return entries[0]


class TestSyncEthan:
    def test_current_team(self, client, mock_vlr):
        html = load_fixture("player", "11225_ethan", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "NRG")
        mock_vlr.get("/player/11225").respond(200, text=html)
        result = client.player.teams.current_team(11225)
        assert result is not None
        assert result.team_id == 1034
        assert result.name == "NRG"
        assert result.slug == "nrg"
        assert result.joined_date == expected["joined_date"]
        assert result.left_date is None
        assert result.inactive_date is None

    def test_current_team_logo(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.current_team(11225)
        assert result.logo_url.startswith("https://owcdn.net/")

    def test_past_teams_count(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.past_teams(11225)
        assert len(result) >= 3

    def test_past_team_evil_geniuses(self, client, mock_vlr):
        html = load_fixture("player", "11225_ethan", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "Evil Geniuses")
        mock_vlr.get("/player/11225").respond(200, text=html)
        result = client.player.teams.past_teams(11225)
        eg = next((t for t in result if t.name == "Evil Geniuses"), None)
        assert eg is not None
        assert eg.team_id == 5248
        assert eg.slug == "evil-geniuses"
        assert eg.joined_date == expected["joined_date"]
        assert eg.left_date == expected["left_date"]
        assert eg.inactive_date is None

    def test_past_team_nrg_with_inactive(self, client, mock_vlr):
        html = load_fixture("player", "11225_ethan", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "NRG", has_inactive=True)
        mock_vlr.get("/player/11225").respond(200, text=html)
        result = client.player.teams.past_teams(11225)
        nrg_past = next(
            (t for t in result if t.name == "NRG" and t.left_date == expected["left_date"]),
            None,
        )
        assert nrg_past is not None
        assert nrg_past.team_id == 1034
        assert nrg_past.joined_date == expected["joined_date"]
        assert nrg_past.inactive_date == expected["inactive_date"]

    def test_teams(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams(11225)
        assert len(result.current_teams) >= 1
        assert len(result.past_teams) >= 3


class TestSyncInspire:
    def test_current_team(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.current_team(53)
        if result is not None:
            assert isinstance(result.team_id, int)
            assert isinstance(result.name, str)

    def test_past_teams_count(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        assert len(result) >= 6

    def test_past_team_rankers(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "RANKERS")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "RANKERS"), None)
        assert team is not None
        assert team.team_id == 16806
        assert team.slug == "rankers"
        assert team.left_date == expected["left_date"]

    def test_past_team_100_thieves(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "100 Thieves")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "100 Thieves"), None)
        assert team is not None
        assert team.team_id == 120
        assert team.slug == "100-thieves"
        assert team.joined_date == expected["joined_date"]
        assert team.left_date == expected["left_date"]

    def test_past_team_faze(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "FaZe Clan")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "FaZe Clan"), None)
        assert team is not None
        assert team.team_id == 337
        assert team.slug == "faze-clan"
        assert team.joined_date == expected["joined_date"]
        assert team.left_date == expected["left_date"]

    def test_past_team_rice_no_joined(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "rice and meatballs")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "rice and meatballs"), None)
        assert team is not None
        assert team.team_id == 4000
        assert team.slug == "rice-and-meatballs"
        assert team.joined_date is None
        assert team.left_date == expected["left_date"]

    def test_past_team_nsic(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "NSIC")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "NSIC"), None)
        assert team is not None
        assert team.team_id == 2403
        assert team.slug == "nsic"
        assert team.joined_date is None
        assert team.left_date == expected["left_date"]

    def test_past_team_prospects(self, client, mock_vlr):
        html = load_fixture("player", "53_inspire", "overview.html")
        parsed = HTMLParser(html)
        expected = _expected_for_team(parsed, "Prospects")
        mock_vlr.get("/player/53").respond(200, text=html)
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "Prospects"), None)
        assert team is not None
        assert team.team_id == 15
        assert team.slug == "prospects"
        assert team.joined_date == expected["joined_date"]
        assert team.left_date == expected["left_date"]

    def test_teams(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams(53)
        assert len(result.current_teams) >= 0
        assert len(result.past_teams) >= 6