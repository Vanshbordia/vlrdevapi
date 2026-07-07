import pytest
from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi


class TestSyncModuleLevel:
    def test_team_roster_nrg(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        result = vlrdevapi.team.roster(1034)
        assert len(result.players) > 0
        assert len(result.staff) > 0

        player = result.players[0]
        assert player.id > 0
        assert player.ign
        assert player.real_name
        assert player.country
        assert player.roles
        assert player.photo_url.startswith("https://")

    def test_team_roster_100_thieves(self, mock_vlr):
        mock_vlr.get("/team/120").respond(200, text=load_fixture("team", "120", "overview_light.html"))

        result = vlrdevapi.team.roster(120)
        assert len(result.players) > 0
        assert len(result.staff) > 0

        captain = next((p for p in result.players if p.is_captain), None)
        assert captain is not None

    def test_team_roster_no_roster(self, mock_vlr):
        mock_vlr.get("/team/17676").respond(200, text=load_fixture("team", "17676", "overview_light.html"))

        from vlrdevapi.exceptions import DataNotFoundError
        with pytest.raises(DataNotFoundError, match="roster not found on team page"):
            vlrdevapi.team.roster(17676)


class TestSyncWithClient:
    def test_team_roster_curried(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team(1034).roster()
        assert len(result.players) > 0

    def test_team_roster_direct(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team.roster(1034)
        assert len(result.players) > 0



