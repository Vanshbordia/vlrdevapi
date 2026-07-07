from unittest.mock import patch

from tests.conftest import load_fixture
import vlrdevapi


class TestSyncLiveMatches:
    def test_live_matches_structure(self, mock_vlr):
        mock_vlr.get("/matches").respond(200, text=load_fixture("matches", "matches.html"))

        with patch("vlrdevapi._matches.common.enrich_team_data_sync"):
            result = vlrdevapi.matches.live()

        assert hasattr(result, "matches")
        assert isinstance(result.matches, list)

        for match in result.matches:
            assert hasattr(match, "match_id")
            assert isinstance(match.match_id, int)
            assert match.match_id > 0
            assert hasattr(match, "url")
            assert isinstance(match.url, str)
            assert match.url.startswith("/")
            assert hasattr(match, "event")
            assert isinstance(match.event, str)
            assert len(match.event) > 0
            assert hasattr(match, "stage")
            assert isinstance(match.stage, str)
            assert hasattr(match, "status")
            assert isinstance(match.status, str)
            assert match.status == "live"
            assert hasattr(match, "datetime")
            assert hasattr(match, "team1")
            assert hasattr(match, "team2")
            for team in [match.team1, match.team2]:
                if team is not None:
                    assert hasattr(team, "id")
                    assert isinstance(team.id, int)
                    assert hasattr(team, "name")
                    assert isinstance(team.name, str)
                    assert hasattr(team, "tag")
                    assert isinstance(team.tag, str)
                    assert hasattr(team, "country_name")
                    assert isinstance(team.country_name, str)


class TestSyncWithClient:
    def test_live_matches_structure(self, mock_vlr):
        mock_vlr.get("/matches").respond(200, text=load_fixture("matches", "matches.html"))

        with patch("vlrdevapi._matches.common.enrich_team_data_sync"):
            with vlrdevapi.VLRClient() as client:
                result = client.matches.live()

        assert hasattr(result, "matches")
        assert isinstance(result.matches, list)




