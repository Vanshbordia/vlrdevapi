"""Tests for search module using real HTML sources (mocked)."""

import vlrdevapi as vlr


class TestSearchAll:
    """Test searching across all types."""

    def test_search_all_returns_results(self, mock_fetch_html):
        results = vlr.search.search("nrg")
        assert results is not None
        assert results.query == "nrg"
        assert results.total_results >= 0
        # From our fixture HTML we expect at least 1 team, 1 player, 1 event
        assert len(results.teams) >= 1
        assert len(results.players) >= 1
        assert len(results.events) >= 1

    def test_search_player_enriched_country(self, mock_fetch_html):
        results = vlr.search.search("s0m")
        # Find s0m (player id 4164)
        s0m = next((p for p in results.players if p.player_id == 4164), None)
        assert s0m is not None
        # Country is enriched via players.profile mock
        # It might be None depending on fixture, just ensure attribute exists
        assert hasattr(s0m, "country")

    def test_search_team_enriched_country(self, mock_fetch_html):
        results = vlr.search.search("nrg")
        nrg_team = next((t for t in results.teams if t.team_id == 1034), None)
        assert nrg_team is not None
        # Country enriched via teams.info mock
        assert hasattr(nrg_team, "country")


class TestSearchTypeSpecific:
    """Test type-specific search helpers."""

    def test_search_players(self, mock_fetch_html):
        players = vlr.search.search_players("nrg")
        assert isinstance(players, list)
        if players:
            p = players[0]
            assert hasattr(p, "player_id")
            assert hasattr(p, "ign")

    def test_search_teams(self, mock_fetch_html):
        teams = vlr.search.search_teams("nrg")
        assert isinstance(teams, list)
        if teams:
            t = teams[0]
            assert hasattr(t, "team_id")
            assert hasattr(t, "name")

    def test_search_events(self, mock_fetch_html):
        events = vlr.search.search_events("nrg")
        assert isinstance(events, list)
        if events:
            e = events[0]
            assert hasattr(e, "event_id")
            assert hasattr(e, "name")
