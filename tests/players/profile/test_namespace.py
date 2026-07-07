from tests.conftest import load_fixture
import vlrdevapi


class TestSyncModuleLevel:
    def test_ethan_profile(self, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.profile(11225)
        assert result.player_id == 11225
        assert result.name == "Ethan"
        assert result.real_name == "Ethan Arnold"
        assert result.country_code == "us"
        assert result.current_team is not None
        assert result.current_team.name == "NRG"
        assert len(result.top_agents) > 0
        assert result.stats_timespan in ("30d", "all")

    def test_yuvi_profile(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.profile(46051)
        assert result.player_id == 46051
        assert result.name != ""
        assert len(result.top_agents) > 0
        assert result.stats_timespan in ("30d", "all")


class TestSyncWithClient:
    def test_ethan_profile(self, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.profile(11225)
        assert result.player_id == 11225
        assert result.name == "Ethan"
        assert result.current_team is not None
        assert result.current_team.name == "NRG"
        assert len(result.top_agents) > 0

    def test_yuvi_profile(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.profile(46051)
        assert result.player_id == 46051
        assert len(result.top_agents) > 0

