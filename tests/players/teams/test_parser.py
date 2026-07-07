from datetime import datetime, timezone

from tests.conftest import load_fixture


class TestSyncEthan:
    def test_current_team(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.current_team(11225)
        assert result is not None
        assert result.team_id == 1034
        assert result.name == "NRG"
        assert result.slug == "nrg"
        assert result.joined_date == datetime(2023, 12, 1, tzinfo=timezone.utc)
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
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.past_teams(11225)
        eg = next((t for t in result if t.name == "Evil Geniuses"), None)
        assert eg is not None
        assert eg.team_id == 5248
        assert eg.slug == "evil-geniuses"
        assert eg.joined_date == datetime(2022, 11, 1, tzinfo=timezone.utc)
        assert eg.left_date == datetime(2023, 12, 1, tzinfo=timezone.utc)
        assert eg.inactive_date is None

    def test_past_team_nrg_with_inactive(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.past_teams(11225)
        nrg_past = next(
            (t for t in result if t.name == "NRG" and t.left_date == datetime(2022, 11, 1, tzinfo=timezone.utc)),
            None,
        )
        assert nrg_past is not None
        assert nrg_past.team_id == 1034
        assert nrg_past.joined_date == datetime(2022, 4, 1, tzinfo=timezone.utc)
        assert nrg_past.inactive_date == datetime(2022, 9, 1, tzinfo=timezone.utc)

    def test_past_team_100_thieves(self, client, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))
        result = client.player.teams.past_teams(11225)
        tt = next((t for t in result if t.name == "100 Thieves"), None)
        assert tt is not None
        assert tt.team_id == 120
        assert tt.slug == "100-thieves"
        assert tt.joined_date == datetime(2021, 3, 1, tzinfo=timezone.utc)
        assert tt.left_date == datetime(2022, 4, 1, tzinfo=timezone.utc)

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
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "RANKERS"), None)
        assert team is not None
        assert team.team_id == 16806
        assert team.slug == "rankers"
        assert team.left_date == datetime(2025, 3, 1, tzinfo=timezone.utc)

    def test_past_team_100_thieves(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "100 Thieves"), None)
        assert team is not None
        assert team.team_id == 120
        assert team.slug == "100-thieves"
        assert team.joined_date == datetime(2022, 1, 1, tzinfo=timezone.utc)
        assert team.left_date == datetime(2022, 2, 1, tzinfo=timezone.utc)

    def test_past_team_faze(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "FaZe Clan"), None)
        assert team is not None
        assert team.team_id == 337
        assert team.slug == "faze-clan"
        assert team.joined_date == datetime(2021, 7, 1, tzinfo=timezone.utc)
        assert team.left_date == datetime(2021, 11, 1, tzinfo=timezone.utc)

    def test_past_team_rice_no_joined(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "rice and meatballs"), None)
        assert team is not None
        assert team.team_id == 4000
        assert team.slug == "rice-and-meatballs"
        assert team.joined_date is None
        assert team.left_date == datetime(2021, 4, 1, tzinfo=timezone.utc)

    def test_past_team_nsic(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "NSIC"), None)
        assert team is not None
        assert team.team_id == 2403
        assert team.slug == "nsic"
        assert team.joined_date is None
        assert team.left_date == datetime(2021, 2, 1, tzinfo=timezone.utc)

    def test_past_team_prospects(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams.past_teams(53)
        team = next((t for t in result if t.name == "Prospects"), None)
        assert team is not None
        assert team.team_id == 15
        assert team.slug == "prospects"
        assert team.joined_date == datetime(2020, 6, 1, tzinfo=timezone.utc)
        assert team.left_date == datetime(2020, 7, 1, tzinfo=timezone.utc)

    def test_teams(self, client, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))
        result = client.player.teams(53)
        assert len(result.current_teams) >= 0
        assert len(result.past_teams) >= 6
