import pytest

from tests.conftest import load_fixture
import vlrdevapi


class TestSyncModuleLevel:
    def test_yuvi_agents_all(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=all").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.agents(46051)
        assert result.timespan == "all"
        assert len(result.agents) > 0

    def test_yuvi_agents_30d(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.agents(46051, timespan="30d")
        assert result.timespan == "30d"
        assert isinstance(result.agents, list)

    def test_yuvi_agents_60d(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=60d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.agents(46051, timespan="60d")
        assert result.timespan == "60d"
        assert len(result.agents) > 0

    def test_yuvi_agents_90d(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=90d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.agents(46051, timespan="90d")
        assert result.timespan == "90d"
        assert len(result.agents) > 0

    def test_invalid_timespan(self):
        with pytest.raises(ValueError):
            vlrdevapi.player.agents(46051, timespan="1y")  # type: ignore


class TestSyncWithClient:
    def test_yuvi_agents_all(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=all").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.agents(46051)
        assert result.timespan == "all"
        assert len(result.agents) > 0

    def test_yuvi_agents_30d(self, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.agents(46051, timespan="30d")
        assert result.timespan == "30d"

    def test_invalid_timespan(self):
        with vlrdevapi.VLRClient() as client:
            with pytest.raises(ValueError):
                client.player.agents(46051, timespan="invalid")


