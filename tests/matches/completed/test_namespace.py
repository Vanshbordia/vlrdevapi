from unittest.mock import patch

from tests.conftest import load_fixture
import vlrdevapi


class TestSyncCompletedMatches:
    def test_completed_matches_structure(self, mock_vlr):
        mock_vlr.get("/matches/results").respond(200, text=load_fixture("matches", "results.html"))

        with patch("vlrdevapi._matches.common.enrich_team_data_sync"):
            result = vlrdevapi.matches.completed()

        assert hasattr(result, "matches")
        assert isinstance(result.matches, list)
        assert hasattr(result, "has_next_page")
        assert isinstance(result.has_next_page, bool)

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
            assert match.status == "completed"
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
                    assert hasattr(team, "score")
                    assert isinstance(team.score, int)
                    assert team.score >= 0
                    assert hasattr(team, "is_winner")
                    assert isinstance(team.is_winner, bool)

    def test_completed_matches_page_parameter(self, mock_vlr):
        mock_vlr.get("/matches/results").respond(200, text=load_fixture("matches", "results.html"))
        mock_vlr.get("/matches/results/?page=2").respond(200, text=load_fixture("matches", "results_page2.html"))

        with patch("vlrdevapi._matches.common.enrich_team_data_sync"):
            result_page1 = vlrdevapi.matches.completed(page=1)
            result_page2 = vlrdevapi.matches.completed(page=2)

        assert hasattr(result_page1, "matches")
        assert hasattr(result_page2, "matches")
        assert hasattr(result_page1, "has_next_page")
        assert hasattr(result_page2, "has_next_page")


class TestSyncWithClient:
    def test_completed_matches_structure(self, mock_vlr):
        mock_vlr.get("/matches/results").respond(200, text=load_fixture("matches", "results.html"))

        with patch("vlrdevapi._matches.common.enrich_team_data_sync"):
            with vlrdevapi.VLRClient() as client:
                result = client.matches.completed()

        assert hasattr(result, "matches")
        assert isinstance(result.matches, list)
        assert hasattr(result, "has_next_page")
        assert isinstance(result.has_next_page, bool)




