import pytest

from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi


class TestSyncModuleLevel:
    def _mock_team(self, mock_vlr, team_id: str, team_int: int):
        light = load_fixture("team", team_id, "overview_light.html")
        dark = load_fixture("team", team_id, "overview_dark.html")
        mock_vlr.get(f"/team/{team_id}", headers={"Cookie": "settings=%7B%22dark_mode%22%3A1%7D"}).respond(200, text=dark)
        mock_vlr.get(f"/team/{team_id}").respond(200, text=light)

    def test_team_info_nrg(self, mock_vlr):
        self._mock_team(mock_vlr, "1034", 1034)
        result = vlrdevapi.team.info(1034)
        assert result.id == 1034
        assert result.name == "NRG"
        assert result.tag == "NRG"
        assert result.country == "United States"
        assert result.is_active is True
        assert result.socials is not None
        assert len(result.socials) >= 1
        assert result.previous_teams is None
        assert result.current_teams is None
        assert result.light_logo_url.startswith("https://")
        assert result.dark_logo_url.startswith("https://")

    def test_team_info_100_thieves(self, mock_vlr):
        self._mock_team(mock_vlr, "120", 120)
        result = vlrdevapi.team.info(120)
        assert result.id == 120
        assert result.name == "100 Thieves"
        assert result.tag == "100T"
        assert result.country == "United States"
        assert result.is_active is True
        assert result.socials is not None
        assert len(result.socials) >= 1
        assert result.previous_teams is None
        assert result.current_teams is None
        assert result.light_logo_url.startswith("https://")
        assert result.dark_logo_url.startswith("https://")

    def test_team_info_m3_champions(self, mock_vlr):
        self._mock_team(mock_vlr, "8326", 8326)

    def test_team_info_gambit(self, mock_vlr):
        self._mock_team(mock_vlr, "682", 682)


class TestSyncWithClient:
    def test_team_info_curried(self, mock_vlr):
        light = load_fixture("team", "1034", "overview_light.html")
        dark = load_fixture("team", "1034", "overview_dark.html")
        mock_vlr.get("/team/1034", headers={"Cookie": "settings=%7B%22dark_mode%22%3A1%7D"}).respond(200, text=dark)
        mock_vlr.get("/team/1034").respond(200, text=light)

        with vlrdevapi.VLRClient() as client:
            result = client.team(1034).info()
        assert result.id == 1034
        assert result.name == "NRG"

    def test_team_info_direct(self, mock_vlr):
        light = load_fixture("team", "1034", "overview_light.html")
        dark = load_fixture("team", "1034", "overview_dark.html")
        mock_vlr.get("/team/1034", headers={"Cookie": "settings=%7B%22dark_mode%22%3A1%7D"}).respond(200, text=dark)
        mock_vlr.get("/team/1034").respond(200, text=light)

        with vlrdevapi.VLRClient() as client:
            result = client.team.info(1034)
        assert result.id == 1034
        assert result.name == "NRG"

