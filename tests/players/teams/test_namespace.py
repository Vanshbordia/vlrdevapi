from datetime import date

from tests.conftest import load_fixture
import vlrdevapi


class TestSyncModuleLevel:
    def test_ethan_current_team(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.teams.current_team(11225)
        assert result is not None
        assert result.team_id == 1034
        assert result.name == "NRG"
        assert result.slug == "nrg"
        assert result.joined_date == date(2023, 12, 1)

    def test_ethan_past_teams(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.teams.past_teams(11225)
        assert len(result) >= 3
        eg = next((t for t in result if t.name == "Evil Geniuses"), None)
        assert eg is not None and eg.team_id == 5248
        tt = next((t for t in result if t.name == "100 Thieves"), None)
        assert tt is not None and tt.team_id == 120

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

