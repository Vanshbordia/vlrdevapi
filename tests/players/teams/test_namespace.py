from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from tests.helpers.expected_from_html import player_team_dates_from_lines
from tests.helpers.fixtures import player_team_texts
import vlrdevapi


class TestSyncModuleLevel:
    def test_ethan_current_team(self, mock_vlr):
        html = load_fixture("player", "11225_ethan", "overview.html")
        parsed = HTMLParser(html)
        expected = player_team_dates_from_lines(player_team_texts(parsed, "NRG")[0])
        mock_vlr.get("/player/11225").respond(200, text=html)

        result = vlrdevapi.player.teams.current_team(11225)
        assert result is not None
        assert result.team_id == 1034
        assert result.name == "NRG"
        assert result.slug == "nrg"
        assert result.joined_date == expected["joined_date"]

    def test_ethan_past_teams(self, mock_vlr):
        html = load_fixture("player", "11225_ethan", "overview.html")
        parsed = HTMLParser(html)
        expected = player_team_dates_from_lines(player_team_texts(parsed, "Evil Geniuses")[0])
        mock_vlr.get("/player/11225").respond(200, text=html)

        result = vlrdevapi.player.teams.past_teams(11225)
        assert len(result) >= 3
        eg = next((t for t in result if t.name == "Evil Geniuses"), None)
        assert eg is not None
        assert eg.team_id == 5248
        assert eg.joined_date == expected["joined_date"]
        assert eg.left_date == expected["left_date"]

    def test_ethan_teams(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.teams(11225)
        assert len(result.current_teams) >= 1
        assert len(result.past_teams) >= 3

    def test_inspire_current_team(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        result = vlrdevapi.player.teams.current_team(53)
        if result is not None:
            assert isinstance(result.team_id, int)

    def test_inspire_past_teams(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        result = vlrdevapi.player.teams.past_teams(53)
        assert len(result) >= 6


class TestSyncWithClient:
    def test_ethan_current_team(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.teams.current_team(11225)
        assert result is not None
        assert result.team_id == 1034
        assert result.name == "NRG"

    def test_ethan_past_teams(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.teams.past_teams(11225)
        assert len(result) >= 3

    def test_ethan_teams(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.teams(11225)
        assert len(result.current_teams) >= 1
        assert len(result.past_teams) >= 3

    def test_inspire_current_team(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.teams.current_team(53)
        if result is not None:
            assert isinstance(result.team_id, int)

    def test_inspire_past_teams(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.teams.past_teams(53)
        assert len(result) >= 6