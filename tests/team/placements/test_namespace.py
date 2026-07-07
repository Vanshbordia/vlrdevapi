from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi


class TestSyncModuleLevel:
    def test_team_placements_nrg(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        result = vlrdevapi.team.placements(1034)
        assert result.team_id == 1034
        assert result.total_winnings is not None
        assert result.total_winnings_currency == "$"
        assert len(result.placements) > 0

        first_placement = result.placements[0]
        assert first_placement.event_id > 0
        assert first_placement.event_name
        assert first_placement.year > 0
        assert len(first_placement.placements) > 0

    def test_team_placements_100_thieves(self, mock_vlr):
        mock_vlr.get("/team/120").respond(200, text=load_fixture("team", "120", "overview_light.html"))

        result = vlrdevapi.team.placements(120)
        assert result.team_id == 120
        assert len(result.placements) > 0

    def test_team_placements_low_tier(self, mock_vlr):
        mock_vlr.get("/team/17676").respond(200, text=load_fixture("team", "17676", "overview_light.html"))

        result = vlrdevapi.team.placements(17676)
        assert result.team_id == 17676
        assert result.total_winnings == 0
        assert len(result.placements) >= 1


class TestSyncWithClient:
    def test_team_placements_curried(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team(1034).placements()
        assert result.team_id == 1034
        assert len(result.placements) > 0

    def test_team_placements_direct(self, mock_vlr):
        mock_vlr.get("/team/1034").respond(200, text=load_fixture("team", "1034", "overview_light.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team.placements(1034)
        assert result.team_id == 1034
        assert len(result.placements) > 0
