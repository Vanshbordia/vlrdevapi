import pytest

from tests.conftest import load_fixture


class TestSyncYuvi:
    @staticmethod
    def _mock_yuvi(mock_vlr):
        mock_vlr.get("/player/46051/?timespan=all").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        mock_vlr.get("/player/46051/?timespan=60d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        mock_vlr.get("/player/46051/?timespan=90d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

    def test_agents_count(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert len(result.agents) > 0

    def test_first_agent_name(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].agent != ""

    def test_first_agent_use(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].use != ""

    def test_first_agent_rounds(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].rounds > 0

    def test_first_agent_rating(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].rating > 0

    def test_first_agent_acs(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].acs > 0

    def test_first_agent_kd(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].kd > 0

    def test_first_agent_adr(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].adr > 0

    def test_first_agent_kast(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].kast != ""

    def test_first_agent_kpr(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].kpr > 0

    def test_first_agent_apr(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].apr is None or result.agents[0].apr >= 0

    def test_first_agent_fkpr(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].fkpr is None or result.agents[0].fkpr >= 0

    def test_first_agent_fdpr(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].fdpr is None or result.agents[0].fdpr >= 0

    def test_first_agent_kills(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].kills > 0

    def test_first_agent_deaths(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].deaths > 0

    def test_first_agent_assists(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].assists is None or result.agents[0].assists >= 0

    def test_first_agent_first_kills(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].first_kills is None or result.agents[0].first_kills >= 0

    def test_first_agent_first_deaths(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.agents[0].first_deaths is None or result.agents[0].first_deaths >= 0

    def test_timespan(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="all")
        assert result.timespan == "all"

    def test_timespan_30d(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="30d")
        assert result.timespan == "30d"

    def test_timespan_60d(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="60d")
        assert result.timespan == "60d"

    def test_timespan_90d(self, client, mock_vlr):
        self._mock_yuvi(mock_vlr)
        result = client.player.agents(46051, timespan="90d")
        assert result.timespan == "90d"

    def test_invalid_timespan(self, client):
        with pytest.raises(ValueError):
            client.player.agents(46051, timespan="1y")


class TestSyncEthan:
    @staticmethod
    def _mock_ethan(mock_vlr):
        mock_vlr.get("/player/11225/?timespan=all").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

    def test_agents_not_empty(self, client, mock_vlr):
        self._mock_ethan(mock_vlr)
        result = client.player.agents(11225, timespan="all")
        assert len(result.agents) > 0

    def test_agent_name_is_string(self, client, mock_vlr):
        self._mock_ethan(mock_vlr)
        result = client.player.agents(11225, timespan="all")
        for agent in result.agents:
            assert isinstance(agent.agent, str)
            assert agent.agent != ""

    def test_timespan_30d(self, client, mock_vlr):
        self._mock_ethan(mock_vlr)
        result = client.player.agents(11225, timespan="30d")
        assert result.timespan == "30d"
