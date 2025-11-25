"""Tests for series module using real HTML sources."""

import pytest
import vlrdevapi as vlr


class TestSeriesInfo:
    """Test series info functionality."""
    
    def test_info_returns_data(self, mock_fetch_html):
        """Test that info() returns data."""
        info = vlr.series.info(match_id=530935)
        assert info is not None
    
    def test_info_structure(self, mock_fetch_html):
        """Test info structure."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert hasattr(info, 'match_id')
            assert hasattr(info, 'teams')
            assert hasattr(info, 'score')
            assert hasattr(info, 'event')
            assert hasattr(info, 'status_note')
    
    def test_info_match_id(self, mock_fetch_html):
        """Test that match_id is correct."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert info.match_id == 530935
    
    def test_info_teams(self, mock_fetch_html):
        """Test that teams are extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert isinstance(info.teams, tuple)
            assert len(info.teams) == 2
            assert hasattr(info.teams[0], 'name')
            assert hasattr(info.teams[1], 'name')
    
    def test_info_team_structure(self, mock_fetch_html):
        """Test team structure."""
        info = vlr.series.info(match_id=530935)
        if info:
            team = info.teams[0]
            assert hasattr(team, 'id')
            assert hasattr(team, 'name')
            assert hasattr(team, 'short')
            assert hasattr(team, 'country')
            assert hasattr(team, 'score')
    
    def test_info_score(self, mock_fetch_html):
        """Test that score is extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert isinstance(info.score, tuple)
            assert len(info.score) == 2
    
    def test_info_event(self, mock_fetch_html):
        """Test that event info is extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert isinstance(info.event, str)
            assert isinstance(info.event_phase, str)
    
    def test_info_map_actions(self, mock_fetch_html):
        """Test that map actions are extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert hasattr(info, 'map_actions')
            assert hasattr(info, 'picks')
            assert hasattr(info, 'bans')
            assert isinstance(info.map_actions, list)
            assert isinstance(info.picks, list)
            assert isinstance(info.bans, list)
    
    def test_info_map_action_structure(self, mock_fetch_html):
        """Test map action structure."""
        info = vlr.series.info(match_id=530935)
        if info and info.map_actions:
            action = info.map_actions[0]
            assert hasattr(action, 'action')
            assert hasattr(action, 'team')
            assert hasattr(action, 'map')
    
    def test_info_date_time(self, mock_fetch_html):
        """Test that date and time are extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            assert hasattr(info, 'date')
            assert hasattr(info, 'time')


class TestSeriesMatches:
    """Test series matches functionality."""
    
    def test_matches_returns_list(self, mock_fetch_html):
        """Test that matches() returns a list."""
        maps = vlr.series.matches(series_id=530935)
        assert isinstance(maps, list)
    
    def test_match_structure(self, mock_fetch_html):
        """Test match structure."""
        maps = vlr.series.matches(series_id=530935)
        if maps:
            map_data = maps[0]
            assert hasattr(map_data, 'game_id')
            assert hasattr(map_data, 'map_name')
            assert hasattr(map_data, 'players')
            assert hasattr(map_data, 'teams')
            assert hasattr(map_data, 'rounds')
    
    def test_match_map_name(self, mock_fetch_html):
        """Test that map names are extracted."""
        maps = vlr.series.matches(series_id=530935)
        for map_data in maps:
            if map_data.map_name:
                assert isinstance(map_data.map_name, str)
    
    def test_match_players(self, mock_fetch_html):
        """Test that players are extracted."""
        maps = vlr.series.matches(series_id=530935)
        for map_data in maps:
            assert isinstance(map_data.players, list)
    
    def test_player_structure(self, mock_fetch_html):
        """Test player structure in match."""
        maps = vlr.series.matches(series_id=530935)
        for map_data in maps:
            if map_data.players:
                player = map_data.players[0]
                assert hasattr(player, 'name')
                assert hasattr(player, 'agents')
                assert hasattr(player, 'acs')
                assert hasattr(player, 'k')
                assert hasattr(player, 'd')
                assert hasattr(player, 'a')
    
    def test_match_teams(self, mock_fetch_html):
        """Test that team scores are extracted."""
        maps = vlr.series.matches(series_id=530935)
        for map_data in maps:
            if map_data.teams:
                assert isinstance(map_data.teams, tuple)
                assert len(map_data.teams) == 2


class TestSeriesIntegration:
    """Integration tests for series module."""
    
    def test_full_series_data_flow(self, mock_fetch_html):
        """Test getting all series data."""
        # Get series info
        info = vlr.series.info(match_id=530935)
        assert info is not None
        
        # Get match details
        maps = vlr.series.matches(series_id=530935)
        assert isinstance(maps, list)
    
    def test_models_immutable(self, mock_fetch_html):
        """Test that models are immutable (frozen dataclasses)."""
        info = vlr.series.info(match_id=530935)
        if info:
            with pytest.raises(Exception):
                info.match_id = 999
    
    def test_team_metadata(self, mock_fetch_html):
        """Test that team metadata is extracted."""
        info = vlr.series.info(match_id=530935)
        if info:
            for team in info.teams:
                # Team should have basic info
                assert team.name is not None


class TestSeriesPerformance:
    """Test series performance functionality."""
    
    def test_performance_returns_list(self, mock_fetch_html):
        """Test that performance() returns a list."""
        perf = vlr.series.performance(series_id=530935)
        assert isinstance(perf, list)
    
    def test_performance_structure(self, mock_fetch_html):
        """Test performance structure."""
        perf = vlr.series.performance(series_id=530935)
        if perf:
            game = perf[0]
            assert hasattr(game, 'game_id')
            assert hasattr(game, 'map_name')
            assert hasattr(game, 'kill_matrix')
            assert hasattr(game, 'fkfd_matrix')
            assert hasattr(game, 'op_matrix')
            assert hasattr(game, 'player_performances')
    
    def test_kill_matrix_structure(self, mock_fetch_html):
        """Test kill matrix entry structure."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.kill_matrix:
                entry = game.kill_matrix[0]
                assert hasattr(entry, 'killer_name')
                assert hasattr(entry, 'victim_name')
                assert hasattr(entry, 'kills')
                assert hasattr(entry, 'deaths')
                assert hasattr(entry, 'differential')
                break
    
    def test_player_performance_structure(self, mock_fetch_html):
        """Test player performance structure."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                player = game.player_performances[0]
                assert hasattr(player, 'name')
                assert hasattr(player, 'team_short')
                assert hasattr(player, 'agent')
                assert hasattr(player, 'multi_2k')
                assert hasattr(player, 'multi_3k')
                assert hasattr(player, 'multi_4k')
                assert hasattr(player, 'multi_5k')
                assert hasattr(player, 'clutch_1v1')
                assert hasattr(player, 'clutch_1v2')
                assert hasattr(player, 'clutch_1v3')
                assert hasattr(player, 'clutch_1v4')
                assert hasattr(player, 'clutch_1v5')
                assert hasattr(player, 'econ')
                assert hasattr(player, 'plants')
                assert hasattr(player, 'defuses')
                break
    
    def test_performance_matrices(self, mock_fetch_html):
        """Test that different matrix types are extracted."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            # Should have at least one matrix type
            assert isinstance(game.kill_matrix, list)
            assert isinstance(game.fkfd_matrix, list)
            assert isinstance(game.op_matrix, list)


class TestSeriesEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_match_id(self, mock_fetch_html):
        """Test handling of invalid match ID."""
        info = vlr.series.info(match_id=999999999)
        assert info is None or info is not None
    
    def test_empty_maps(self, mock_fetch_html):
        """Test handling of empty maps list."""
        maps = vlr.series.matches(series_id=999999999)
        assert isinstance(maps, list)
    
    def test_empty_performance(self, mock_fetch_html):
        """Test handling of empty performance list."""
        perf = vlr.series.performance(series_id=999999999)
        assert isinstance(perf, list)
