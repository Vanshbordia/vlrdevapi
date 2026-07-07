from tests.conftest import load_fixture


class TestSyncEthan:
    def test_player_id(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.player_id == 11225

    def test_name(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.name == "Ethan"

    def test_real_name(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.real_name == "Ethan Arnold"

    def test_country_code(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.country_code == "us"

    def test_img(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.img != ""

    def test_current_team(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.current_team is not None
        assert result.current_team.name == "NRG"
        assert result.current_team.team_id == 1034

    def test_top_agents_not_empty(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert len(result.top_agents) > 0

    def test_first_agent_name(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.top_agents[0].agent != ""

    def test_first_agent_rounds(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.top_agents[0].rounds > 0

    def test_first_agent_rating(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.top_agents[0].rating > 0

    def test_first_agent_acs(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.top_agents[0].acs > 0

    def test_stats_timespan(self, client, mock_vlr):
        mock_vlr.get("/player/11225/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(11225)
        assert result.stats_timespan in ("30d", "all")


class TestSyncYuvi:
    def test_player_id(self, client, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(46051)
        assert result.player_id == 46051

    def test_name(self, client, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(46051)
        assert result.name != ""

    def test_top_agents_not_empty(self, client, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(46051)
        assert len(result.top_agents) > 0

    def test_stats_timespan(self, client, mock_vlr):
        mock_vlr.get("/player/46051/?timespan=30d").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.profile(46051)
        assert result.stats_timespan in ("30d", "all")
