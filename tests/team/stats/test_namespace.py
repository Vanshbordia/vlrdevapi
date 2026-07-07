from datetime import date
from unittest.mock import patch
from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi


def _stats_fixture(team_id: int) -> HTMLParser:
    return HTMLParser(load_fixture("team", str(team_id), "stats.html"))


class TestSyncModuleLevel:
    def test_team_stats_nrg(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            result = vlrdevapi.team.stats(1034)
        assert result.team_id == 1034
        assert len(result.maps) > 0

        for map_stat in result.maps:
            assert map_stat.games_played > 0
            assert map_stat.win_rate is None or map_stat.win_rate >= 0.0
            assert map_stat.wins is None or map_stat.wins >= 0
            assert map_stat.losses is None or map_stat.losses >= 0

    def test_team_stats_with_last_days(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            result = vlrdevapi.team.stats(1034, last_days=30)
        assert result.team_id == 1034
        assert len(result.maps) >= 0

    def test_team_stats_with_date_range(self, mock_vlr):
        mock_vlr.get("/team/stats/1034/?date_start=2025-01-01&date_end=2025-12-31").respond(
            200, text=load_fixture("team", "1034", "stats_date_range.html")
        )

        result = vlrdevapi.team.stats(
            1034,
            date_start=date(2025, 1, 1),
            date_end=date(2025, 12, 31),
        )
        assert result.team_id == 1034
        assert len(result.maps) >= 0

    def test_team_stats_team_with_data(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(17676)):
            result = vlrdevapi.team.stats(17676)
        assert result.team_id == 17676
        assert len(result.maps) >= 0

    def test_team_stats_agent_composition_none(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            result = vlrdevapi.team.stats(1034, agent_composition="none")
        assert result.team_id == 1034
        for map_stat in result.maps:
            assert map_stat.compositions is None

    def test_team_stats_agent_composition_basic(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            result = vlrdevapi.team.stats(1034, agent_composition="basic")
        assert result.team_id == 1034
        assert len(result.maps) > 0

        for map_stat in result.maps:
            if map_stat.compositions:
                for comp in map_stat.compositions:
                    assert len(comp.agents) == 5
                    assert comp.games_played > 0
                    assert comp.wins + comp.losses == comp.games_played
                    assert comp.matches is None
                break


class TestSyncWithClient:
    def test_team_stats_curried(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).stats()
        assert result.team_id == 1034
        assert len(result.maps) > 0

    def test_team_stats_direct(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            with vlrdevapi.VLRClient() as client:
                result = client.team.stats(1034)
        assert result.team_id == 1034
        assert len(result.maps) > 0

    def test_team_stats_curried_with_filters(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).stats(last_days=60)
        assert result.team_id == 1034

    def test_team_stats_with_agent_composition_basic(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).stats(agent_composition="basic")
        assert result.team_id == 1034
        assert len(result.maps) > 0

        for map_stat in result.maps:
            if map_stat.compositions:
                assert len(map_stat.compositions) > 0
                break

    def test_team_stats_with_agent_composition_detailed(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_stats_fixture(1034)):
            with vlrdevapi.VLRClient() as client:
                result = client.team(1034).stats(agent_composition="detailed")
        assert result.team_id == 1034
        assert len(result.maps) > 0

        for map_stat in result.maps:
            if map_stat.compositions:
                for comp in map_stat.compositions:
                    if comp.games_played > 0:
                        assert comp.matches is not None
                        break
                break

