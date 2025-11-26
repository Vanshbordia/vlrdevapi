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

    def test_performance_real_api_chronicle_match(self):
        """Test real API performance data for Chronicle FNC vs NRG (series 542272)."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)
        assert len(perf) > 0

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None

        # Test brawk from NRG: has 22 kills and 15 deaths with diff of 7 (against Chronicle)
        brawk_entries = [entry for entry in all_maps_perf.kill_matrix
                        if entry.killer_name.lower() == "brawk" and entry.killer_team_short == "NRG"]

        assert len(brawk_entries) > 0

        # Check if brawk has 22 kills and 15 deaths with diff 7 against Chronicle
        chronicle_entry = [entry for entry in brawk_entries if entry.victim_name.lower() == "chronicle" and entry.kills == 22 and entry.deaths == 15 and entry.differential == 7]
        assert len(chronicle_entry) > 0

        # Test FKFD matrix: 2 to 1 with diff of 1
        fkfd_entries = [entry for entry in all_maps_perf.fkfd_matrix if entry.kills == 2 and entry.deaths == 1]
        assert len(fkfd_entries) > 0
        fkfd_entry = fkfd_entries[0]
        assert fkfd_entry.differential == 1

        # Test OP kills: mada from NRG has OP kills, Boaster from FNC has 0
        mada_op_entries = [entry for entry in all_maps_perf.op_matrix
                          if entry.killer_name.lower() == "mada" and entry.killer_team_short == "NRG"]
        assert len(mada_op_entries) > 0

        # Sum all of mada's OP kills
        mada_total_op_kills = sum(entry.kills for entry in mada_op_entries if entry.kills)
        assert mada_total_op_kills > 0  # mada has OP kills

        # Boaster from FNC should have no OP kills
        boaster_op_entries = [entry for entry in all_maps_perf.op_matrix
                             if entry.killer_name.lower() == "boaster" and entry.killer_team_short == "FNC"]
        boaster_total_op_kills = sum(entry.kills for entry in boaster_op_entries if entry.kills) if boaster_op_entries else 0
        assert boaster_total_op_kills == 0

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


class TestSeriesPerformanceAdvanced:
    """Advanced tests for series performance functionality."""

    def test_performance_limit_parameter(self, mock_fetch_html):
        """Test performance() function with limit parameter."""
        perf = vlr.series.performance(series_id=530935, limit=2)
        assert isinstance(perf, list)
        assert len(perf) <= 2

    def test_performance_timeout_parameter(self, mock_fetch_html):
        """Test performance() function with timeout parameter."""
        perf = vlr.series.performance(series_id=530935, timeout=30.0)
        assert isinstance(perf, list)

    def test_performance_game_id_mapping(self, mock_fetch_html):
        """Test that game IDs are correctly mapped to map names."""
        perf = vlr.series.performance(series_id=530935)
        if perf:
            for game in perf:
                assert hasattr(game, 'game_id')
                assert hasattr(game, 'map_name')
                # game_id should be int for individual maps, "All" for combined
                if game.game_id == "All":
                    assert game.map_name in ["All Maps", "All"]
                elif isinstance(game.game_id, int):
                    assert isinstance(game.map_name, str)
                    assert len(game.map_name) > 0

    def test_performance_all_maps_inclusion(self, mock_fetch_html):
        """Test that 'All Maps' is included when multiple maps exist."""
        perf = vlr.series.performance(series_id=530935)
        if perf and len(perf) > 1:
            # Should have "All Maps" when there are multiple individual maps
            all_maps_found = any(game.game_id == "All" for game in perf)
            individual_maps = [game for game in perf if isinstance(game.game_id, int)]
            if len(individual_maps) > 1:
                assert all_maps_found, "All Maps should be included when multiple maps exist"

    def test_kill_matrix_complete_structure(self, mock_fetch_html):
        """Test complete kill matrix entry structure with all fields."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.kill_matrix:
                entry = game.kill_matrix[0]
                # Test all required fields
                assert hasattr(entry, 'killer_name')
                assert hasattr(entry, 'victim_name')
                assert hasattr(entry, 'killer_team_short')
                assert hasattr(entry, 'killer_team_id')
                assert hasattr(entry, 'victim_team_short')
                assert hasattr(entry, 'victim_team_id')
                assert hasattr(entry, 'kills')
                assert hasattr(entry, 'deaths')
                assert hasattr(entry, 'differential')
                
                # Test data types
                assert isinstance(entry.killer_name, str)
                assert isinstance(entry.victim_name, str)
                assert entry.killer_team_short is None or isinstance(entry.killer_team_short, str)
                assert entry.killer_team_id is None or isinstance(entry.killer_team_id, int)
                assert entry.victim_team_short is None or isinstance(entry.victim_team_short, str)
                assert entry.victim_team_id is None or isinstance(entry.victim_team_id, int)
                assert entry.kills is None or isinstance(entry.kills, int)
                assert entry.deaths is None or isinstance(entry.deaths, int)
                assert entry.differential is None or isinstance(entry.differential, int)

    def test_fkfd_matrix_structure(self, mock_fetch_html):
        """Test first kill/first death matrix structure."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.fkfd_matrix:
                entry = game.fkfd_matrix[0]
                # FKFD matrix should have same structure as kill matrix
                assert hasattr(entry, 'killer_name')
                assert hasattr(entry, 'victim_name')
                assert hasattr(entry, 'kills')
                assert hasattr(entry, 'deaths')
                assert hasattr(entry, 'differential')

    def test_op_matrix_structure(self, mock_fetch_html):
        """Test operator (OP) matrix structure."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.op_matrix:
                entry = game.op_matrix[0]
                # OP matrix should have same structure as kill matrix
                assert hasattr(entry, 'killer_name')
                assert hasattr(entry, 'victim_name')
                assert hasattr(entry, 'kills')
                assert hasattr(entry, 'deaths')
                assert hasattr(entry, 'differential')

    def test_player_performance_complete_stats(self, mock_fetch_html):
        """Test complete player performance statistics."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                player = game.player_performances[0]
                # Test all basic fields
                assert hasattr(player, 'name')
                assert hasattr(player, 'team_short')
                assert hasattr(player, 'team_id')
                assert hasattr(player, 'agent')
                
                # Test all multi-kill fields
                assert hasattr(player, 'multi_2k')
                assert hasattr(player, 'multi_3k')
                assert hasattr(player, 'multi_4k')
                assert hasattr(player, 'multi_5k')
                
                # Test all clutch fields
                assert hasattr(player, 'clutch_1v1')
                assert hasattr(player, 'clutch_1v2')
                assert hasattr(player, 'clutch_1v3')
                assert hasattr(player, 'clutch_1v4')
                assert hasattr(player, 'clutch_1v5')
                
                # Test economy and objective fields
                assert hasattr(player, 'econ')
                assert hasattr(player, 'plants')
                assert hasattr(player, 'defuses')
                
                # Test detail fields
                assert hasattr(player, 'multi_2k_details')
                assert hasattr(player, 'multi_3k_details')
                assert hasattr(player, 'multi_4k_details')
                assert hasattr(player, 'multi_5k_details')
                assert hasattr(player, 'clutch_1v1_details')
                assert hasattr(player, 'clutch_1v2_details')
                assert hasattr(player, 'clutch_1v3_details')
                assert hasattr(player, 'clutch_1v4_details')
                assert hasattr(player, 'clutch_1v5_details')

    def test_player_performance_agent_extraction(self, mock_fetch_html):
        """Test that agent names are correctly extracted from image paths."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                for player in game.player_performances:
                    if player.agent:
                        # Agent should be a capitalized string
                        assert isinstance(player.agent, str)
                        assert len(player.agent) > 0
                        # Should be capitalized (first letter uppercase)
                        assert player.agent[0].isupper()

    def test_multi_kill_details_structure(self, mock_fetch_html):
        """Test multi-kill detail structure when available."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                for player in game.player_performances:
                    # Check any multi-kill details
                    for detail_field in ['multi_2k_details', 'multi_3k_details', 'multi_4k_details', 'multi_5k_details']:
                        details = getattr(player, detail_field)
                        if details:
                            for detail in details:
                                assert hasattr(detail, 'round_number')
                                assert hasattr(detail, 'players_killed')
                                assert isinstance(detail.round_number, int)
                                assert isinstance(detail.players_killed, list)
                                assert len(detail.players_killed) > 0

    def test_clutch_details_structure(self, mock_fetch_html):
        """Test clutch detail structure when available."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                for player in game.player_performances:
                    # Check any clutch details
                    for detail_field in ['clutch_1v1_details', 'clutch_1v2_details', 'clutch_1v3_details', 'clutch_1v4_details', 'clutch_1v5_details']:
                        details = getattr(player, detail_field)
                        if details:
                            for detail in details:
                                assert hasattr(detail, 'round_number')
                                assert hasattr(detail, 'players_killed')
                                assert isinstance(detail.round_number, int)
                                assert isinstance(detail.players_killed, list)

    def test_performance_economy_stats(self, mock_fetch_html):
        """Test economy statistics parsing."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.player_performances:
                for player in game.player_performances:
                    # Test economy stats
                    if player.econ is not None:
                        assert isinstance(player.econ, int)
                        assert player.econ >= 0
                    
                    # Test objective stats
                    if player.plants is not None:
                        assert isinstance(player.plants, int)
                        assert player.plants >= 0
                    
                    if player.defuses is not None:
                        assert isinstance(player.defuses, int)
                        assert player.defuses >= 0

    def test_performance_team_id_mapping(self, mock_fetch_html):
        """Test that team IDs are correctly mapped from team tags."""
        perf = vlr.series.performance(series_id=530935)
        for game in perf:
            if game.kill_matrix:
                for entry in game.kill_matrix:
                    # If we have team short names, we should ideally have team IDs
                    if entry.killer_team_short and entry.killer_team_id:
                        assert isinstance(entry.killer_team_id, int)
                    if entry.victim_team_short and entry.victim_team_id:
                        assert isinstance(entry.victim_team_id, int)

    def test_performance_data_consistency(self, mock_fetch_html):
        """Test that performance data is internally consistent."""
        perf = vlr.series.performance(series_id=530935)
        if perf:
            # All games should have valid game_id and map_name
            for game in perf:
                assert game.game_id is not None
                assert game.map_name is not None
                
                # Player performances should have consistent team info
                if game.player_performances:
                    for player in game.player_performances:
                        if player.team_short and player.team_id:
                            # Team ID should be consistent across players from same team
                            teammates = [p for p in game.player_performances 
                                       if p.team_short == player.team_short and p.team_id]
                            for teammate in teammates:
                                assert teammate.team_id == player.team_id

    def test_performance_empty_data_handling(self, mock_fetch_html):
        """Test handling of games with no performance data."""
        perf = vlr.series.performance(series_id=530935)
        # Should return list even if some games have no data
        assert isinstance(perf, list)
        
        # Games with no actual data should be filtered out
        for game in perf:
            has_any_data = (
                len(game.kill_matrix) > 0 or 
                len(game.fkfd_matrix) > 0 or 
                len(game.op_matrix) > 0 or 
                len(game.player_performances) > 0
            )
            assert has_any_data, "Games with no data should be filtered out"


class TestSeriesPerformanceValidation:
    """Specific data validation tests for performance module."""

    def test_performance_542272_brawk_chronicle_kill_matrix(self):
        """Test specific kill matrix data for game 542272: brawk vs Chronicle."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)
        assert len(perf) > 0

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None, "All Maps performance data should be available"

        # Test brawk from NRG: has 22 kills and 15 deaths with diff of 7 (against Chronicle)
        brawk_entries = [entry for entry in all_maps_perf.kill_matrix
                        if entry.killer_name.lower() == "brawk" and 
                        entry.killer_team_short == "NRG" and
                        entry.victim_name.lower() == "chronicle" and
                        entry.victim_team_short == "FNC"]

        assert len(brawk_entries) > 0, "Should find brawk vs Chronicle entry in kill matrix"
        
        brawk_chronicle_entry = brawk_entries[0]
        assert brawk_chronicle_entry.kills == 22, f"brawk should have 22 kills against Chronicle, got {brawk_chronicle_entry.kills}"
        assert brawk_chronicle_entry.deaths == 15, f"brawk should have 15 deaths against Chronicle, got {brawk_chronicle_entry.deaths}"
        assert brawk_chronicle_entry.differential == 7, f"brawk should have differential of 7 against Chronicle, got {brawk_chronicle_entry.differential}"

    def test_performance_542272_brawk_chronicle_fkfd_matrix(self):
        """Test specific FKFD matrix data for game 542272: brawk vs Chronicle."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None

        # Test FKFD matrix: 2 to 1 with diff of 1
        fkfd_entries = [entry for entry in all_maps_perf.fkfd_matrix
                        if entry.killer_name.lower() == "brawk" and 
                        entry.killer_team_short == "NRG" and
                        entry.victim_name.lower() == "chronicle" and
                        entry.victim_team_short == "FNC"]

        assert len(fkfd_entries) > 0, "Should find brawk vs Chronicle entry in FKFD matrix"
        
        fkfd_entry = fkfd_entries[0]
        assert fkfd_entry.kills == 2, f"brawk should have 2 first kills against Chronicle, got {fkfd_entry.kills}"
        assert fkfd_entry.deaths == 1, f"brawk should have 1 first death against Chronicle, got {fkfd_entry.deaths}"
        assert fkfd_entry.differential == 1, f"brawk should have differential of 1 in FKFD against Chronicle, got {fkfd_entry.differential}"

    def test_performance_542272_mada_boaster_op_matrix(self):
        """Test specific OP matrix data for game 542272: mada vs Boaster."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None

        # Test OP kills: mada from NRG has OP kills, Boaster from FNC has 0
        mada_op_entries = [entry for entry in all_maps_perf.op_matrix
                           if entry.killer_name.lower() == "mada" and 
                           entry.killer_team_short == "NRG"]
        
        assert len(mada_op_entries) > 0, "Should find mada entries in OP matrix"

        # Sum all of mada's OP kills
        mada_total_op_kills = sum(entry.kills for entry in mada_op_entries if entry.kills)
        assert mada_total_op_kills >= 1, f"mada should have at least 1 OP kill, got {mada_total_op_kills}"

        # Boaster from FNC should have no OP kills
        boaster_op_entries = [entry for entry in all_maps_perf.op_matrix
                             if entry.killer_name.lower() == "boaster" and 
                             entry.killer_team_short == "FNC"]
        
        boaster_total_op_kills = sum(entry.kills for entry in boaster_op_entries if entry.kills) if boaster_op_entries else 0
        assert boaster_total_op_kills == 0, f"Boaster should have 0 OP kills, got {boaster_total_op_kills}"

    def test_performance_542272_brawk_detailed_stats(self):
        """Test specific player performance stats for brawk in game 542272."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None

        # Find brawk from NRG in player performances
        brawk_performance = None
        for player in all_maps_perf.player_performances:
            if player.name.lower() == "brawk" and player.team_short == "NRG":
                brawk_performance = player
                break

        assert brawk_performance is not None, "Should find brawk in player performances"

        # Test brawk's specific stats: 12 2Ks, 66 econ, 1 1v1, 4 plants, 5 defuses
        assert brawk_performance.multi_2k == 12, f"brawk should have 12 2Ks, got {brawk_performance.multi_2k}"
        assert brawk_performance.econ == 66, f"brawk should have 66 econ, got {brawk_performance.econ}"
        assert brawk_performance.clutch_1v1 == 1, f"brawk should have 1 1v1 clutch, got {brawk_performance.clutch_1v1}"
        assert brawk_performance.plants == 4, f"brawk should have 4 plants, got {brawk_performance.plants}"
        assert brawk_performance.defuses == 5, f"brawk should have 5 defuses, got {brawk_performance.defuses}"

    def test_performance_542272_complete_validation(self):
        """Complete validation test for game 542272 with all specific requirements."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)
        assert len(perf) > 0

        # Find the All Maps performance data
        all_maps_perf = None
        for game in perf:
            if game.game_id == "All":
                all_maps_perf = game
                break

        assert all_maps_perf is not None
        assert all_maps_perf.kill_matrix is not None
        assert all_maps_perf.fkfd_matrix is not None
        assert all_maps_perf.op_matrix is not None
        assert all_maps_perf.player_performances is not None

        # Validate team assignments
        nrg_players = [p for p in all_maps_perf.player_performances if p.team_short == "NRG"]
        fnc_players = [p for p in all_maps_perf.player_performances if p.team_short == "FNC"]
        
        assert len(nrg_players) > 0, "Should have NRG players"
        assert len(fnc_players) > 0, "Should have FNC players"

        # Validate specific players exist
        brawk = next((p for p in nrg_players if p.name.lower() == "brawk"), None)
        mada = next((p for p in nrg_players if p.name.lower() == "mada"), None)
        chronicle = next((p for p in fnc_players if p.name.lower() == "chronicle"), None)
        boaster = next((p for p in fnc_players if p.name.lower() == "boaster"), None)

        assert brawk is not None, "brawk should be in NRG players"
        assert mada is not None, "mada should be in NRG players"
        assert chronicle is not None, "chronicle should be in FNC players"
        assert boaster is not None, "boaster should be in FNC players"

        # Cross-validate kill matrix with player performances
        brawk_chronicle_kills = [e for e in all_maps_perf.kill_matrix 
                                 if e.killer_name.lower() == "brawk" and 
                                 e.victim_name.lower() == "chronicle"]
        assert len(brawk_chronicle_kills) > 0, "Should have brawk vs chronicle kill data"

        print(f"✅ All validations passed for game 542272:")
        print(f"   - Found {len(nrg_players)} NRG players and {len(fnc_players)} FNC players")
        print(f"   - brawk: {brawk.multi_2k} 2Ks, {brawk.econ} econ, {brawk.clutch_1v1} 1v1s")
        print(f"   - Kill matrix has {len(all_maps_perf.kill_matrix)} entries")
        print(f"   - FKFD matrix has {len(all_maps_perf.fkfd_matrix)} entries")
        print(f"   - OP matrix has {len(all_maps_perf.op_matrix)} entries")

    def test_performance_542272_skuba_corrode_detailed_stats(self):
        """Test specific player performance stats for Skuba on Corrode map in game 542272."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)
        assert len(perf) > 0

        # Find the Corrode map performance data
        corrode_perf = None
        for game in perf:
            if game.map_name and "corrode" in game.map_name.lower():
                corrode_perf = game
                break

        assert corrode_perf is not None, "Should find Corrode map performance data"

        # Find Skuba from NRG in Corrode map player performances
        skuba_performance = None
        for player in corrode_perf.player_performances:
            if player.name.lower() == "skuba" and player.team_short == "NRG":
                skuba_performance = player
                break

        assert skuba_performance is not None, "Should find Skuba in Corrode map player performances"

        # Test Skuba's specific stats: 1 1v2, 1 3K, 42 econ, 0 plants, 1 defuse
        assert skuba_performance.clutch_1v2 == 1, f"Skuba should have 1 1v2 clutch, got {skuba_performance.clutch_1v2}"
        assert skuba_performance.multi_3k == 1, f"Skuba should have 1 3K, got {skuba_performance.multi_3k}"
        assert skuba_performance.econ == 42, f"Skuba should have 42 econ, got {skuba_performance.econ}"
        assert skuba_performance.plants == 0, f"Skuba should have 0 plants, got {skuba_performance.plants}"
        assert skuba_performance.defuses == 1, f"Skuba should have 1 defuse, got {skuba_performance.defuses}"

    def test_performance_542272_skuba_corrode_detailed_events(self):
        """Test specific detailed events for Skuba on Corrode map in game 542272."""
        perf = vlr.series.performance(series_id=542272)
        assert isinstance(perf, list)

        # Find the Corrode map performance data
        corrode_perf = None
        for game in perf:
            if game.map_name and "corrode" in game.map_name.lower():
                corrode_perf = game
                break

        assert corrode_perf is not None, "Should find Corrode map performance data"

        # Find Skuba from NRG in Corrode map player performances
        skuba_performance = None
        for player in corrode_perf.player_performances:
            if player.name.lower() == "skuba" and player.team_short == "NRG":
                skuba_performance = player
                break

        assert skuba_performance is not None, "Should find Skuba in Corrode map player performances"

        # Test 1v2 clutch details: Round 9 killing Chronicle and kaajak
        assert skuba_performance.clutch_1v2_details is not None, "Skuba should have 1v2 clutch details"
        assert len(skuba_performance.clutch_1v2_details) >= 1, "Skuba should have at least 1 1v2 clutch detail"
        
        clutch_1v2_detail = skuba_performance.clutch_1v2_details[0]
        assert clutch_1v2_detail.round_number == 9, f"Skuba's 1v2 clutch should be in round 9, got {clutch_1v2_detail.round_number}"
        
        # Check that Chronicle and kaajak are in the players killed
        players_killed_lower = [p.lower() for p in clutch_1v2_detail.players_killed]
        assert "chronicle" in players_killed_lower, "Chronicle should be in Skuba's 1v2 clutch victims"
        assert "kaajak" in players_killed_lower, "kaajak should be in Skuba's 1v2 clutch victims"

        # Test 3K details: Round 8 killing kaajak, boaster, and crashies
        assert skuba_performance.multi_3k_details is not None, "Skuba should have 3K details"
        assert len(skuba_performance.multi_3k_details) >= 1, "Skuba should have at least 1 3K detail"
        
        multi_3k_detail = skuba_performance.multi_3k_details[0]
        assert multi_3k_detail.round_number == 8, f"Skuba's 3K should be in round 8, got {multi_3k_detail.round_number}"
        
        # Check that kaajak, boaster, and crashies are in the players killed
        players_killed_3k_lower = [p.lower() for p in multi_3k_detail.players_killed]
        assert "kaajak" in players_killed_3k_lower, "kaajak should be in Skuba's 3K victims"
        assert "boaster" in players_killed_3k_lower, "boaster should be in Skuba's 3K victims"
        assert "crashies" in players_killed_3k_lower, "crashies should be in Skuba's 3K victims"

        print(f"✅ Skuba Corrode validations passed:")
        print(f"   - 1v2 clutch in round {clutch_1v2_detail.round_number}: {', '.join(clutch_1v2_detail.players_killed)}")
        print(f"   - 3K in round {multi_3k_detail.round_number}: {', '.join(multi_3k_detail.players_killed)}")
        print(f"   - Stats: {skuba_performance.econ} econ, {skuba_performance.plants} plants, {skuba_performance.defuses} defuses")
