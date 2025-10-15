"""Robust validation tests using real HTML sources to verify actual data extraction."""

import pytest
import vlrdevapi as vlr


class TestRealPlayerData:
    """Test that real player data is extracted correctly from HTML."""
    
    def test_player_profile_s0m(self, mock_fetch_html):
        """Test s0m's profile data from real HTML."""
        profile = vlr.players.profile(player_id=4164)
        
        assert profile is not None
        assert profile.player_id == 4164
        assert profile.handle == "s0m"
        assert profile.real_name == "Sam Oh"
        assert profile.country == "United States"
        
    def test_player_has_teams(self, mock_fetch_html):
        """Test that player has team information."""
        profile = vlr.players.profile(player_id=4164)
        
        if profile:
            # Should have either current or past teams
            assert len(profile.current_teams) > 0 or len(profile.past_teams) > 0
    
    def test_player_agent_stats_has_data(self, mock_fetch_html):
        """Test that agent stats contain actual agent names.
        Normalizes names to handle variants like 'KAY/O' vs 'kayo'.
        Uses player 17397 (noia) for timespan fixtures.
        """
        import re
        
        def norm(name: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", name.lower()) if name else ""
        
        stats = vlr.players.agent_stats(player_id=17397)
        assert len(stats) > 0
        
        # Valid Valorant agents (normalized)
        valid_agents = [
            "Astra","Breach","Brimstone","Chamber","Clove","Cypher","Deadlock","Fade","Gekko","Harbor","Iso","Jett","KAY/O","Killjoy","Neon","Omen","Phoenix","Raze","Reyna","Sage","Skye","Sova","Viper","Yoru","Vyse","Tejo","Waylay","Veto"
        ]
        valid_norm = {norm(a) for a in valid_agents}
        
        for stat in stats:
            if stat.agent:
                agent_norm = norm(stat.agent)
                # Allow 'All' aggregate and normalized valid names
                assert agent_norm in valid_norm or agent_norm == norm("All")


class TestRealMatchData:
    """Test that real match data is extracted correctly."""
    
    def test_upcoming_matches_have_teams(self, mock_fetch_html):
        """Test that upcoming matches have valid team names."""
        matches = vlr.matches.upcoming(limit=5)
        
        for match in matches:
            assert match.team1 is not None
            assert match.team2 is not None
            assert match.team1.name is not None
            assert match.team2.name is not None
            assert len(match.team1.name) > 0
            assert len(match.team2.name) > 0
            # Team names should not be just whitespace
            assert match.team1.name.strip() == match.team1.name
            assert match.team2.name.strip() == match.team2.name
    
    def test_completed_matches_have_scores(self, mock_fetch_html):
        """Test that completed matches have valid scores."""
        matches = vlr.matches.completed(limit=5)
        
        for match in matches:
            if match.status == "completed":
                # At least one team should have a score
                assert match.team1.score is not None or match.team2.score is not None
                # Scores should be non-negative integers
                if match.team1.score is not None:
                    assert isinstance(match.team1.score, int)
                    assert match.team1.score >= 0
                if match.team2.score is not None:
                    assert isinstance(match.team2.score, int)
                    assert match.team2.score >= 0
    
    def test_matches_have_events(self, mock_fetch_html):
        """Test that matches have event information."""
        matches = vlr.matches.upcoming(limit=5)
        
        for match in matches:
            assert match.event is not None
            assert len(match.event) > 0


class TestRealSeriesData:
    """Test that real series data is extracted correctly."""
    
    def test_series_has_teams(self, mock_fetch_html):
        """Test that series has team information."""
        info = vlr.series.info(match_id=530935)
        
        if info:
            assert len(info.teams) == 2
            assert info.teams[0].name is not None
            assert info.teams[1].name is not None
            assert len(info.teams[0].name) > 0
            assert len(info.teams[1].name) > 0
    
    def test_series_has_event_info(self, mock_fetch_html):
        """Test that series has event information."""
        info = vlr.series.info(match_id=530935)
        
        if info:
            assert info.event is not None
            assert len(info.event) > 0
            assert info.event_phase is not None
    
    def test_series_maps_have_names(self, mock_fetch_html):
        """Test that series maps have valid map names."""
        maps = vlr.series.matches(series_id=530935)
        
        valid_map_names = ["Ascent", "Bind", "Haven", "Split", "Icebox", 
                          "Breeze", "Fracture", "Pearl", "Lotus", "Sunset", "All"]
        
        for map_data in maps:
            if map_data.map_name and map_data.map_name != "All":
                # Map name should be one of the valid Valorant maps
                assert any(valid_map.lower() in map_data.map_name.lower() 
                          for valid_map in valid_map_names)


class TestRealEventData:
    """Test that real event data is extracted correctly."""
    
    def test_events_list_has_names(self, mock_fetch_html):
        """Test that events have valid names."""
        events = vlr.events.list_events(tier="vct")
        
        for event in events:
            assert event.name is not None
            assert len(event.name) > 0
            # Name should not be just numbers
            assert not event.name.isdigit()
    
    def test_events_have_valid_status(self, mock_fetch_html):
        """Test that events have valid status."""
        events = vlr.events.list_events()
        
        valid_statuses = ["upcoming", "ongoing", "completed"]
        for event in events:
            assert event.status in valid_statuses
    
    def test_event_info_has_details(self, mock_fetch_html):
        """Test that event info has details."""
        info = vlr.events.info(event_id=2498)
        
        if info:
            assert info.name is not None
            assert len(info.name) > 0
            assert info.id == 2498
    
    def test_event_matches_have_teams(self, mock_fetch_html):
        """Test that event matches have team information."""
        matches = vlr.events.matches(event_id=2498)
        
        for match in matches:
            assert len(match.teams) == 2
            assert match.teams[0].name is not None
            assert match.teams[1].name is not None


class TestDataConsistency:
    """Test data consistency across modules."""
    
    def test_match_ids_are_unique(self, mock_fetch_html):
        """Test that match IDs are unique in a list."""
        matches = vlr.matches.upcoming(limit=10)
        
        match_ids = [m.match_id for m in matches]
        # All match IDs should be unique
        assert len(match_ids) == len(set(match_ids))
    
    def test_player_id_consistency(self, mock_fetch_html):
        """Test that player ID is consistent."""
        profile = vlr.players.profile(player_id=457)
        
        if profile:
            assert profile.player_id == 457
    
    def test_event_id_consistency(self, mock_fetch_html):
        """Test that event ID is consistent."""
        info = vlr.events.info(event_id=2498)
        
        if info:
            assert info.id == 2498
        
        matches = vlr.events.matches(event_id=2498)
        for match in matches:
            assert match.event_id == 2498


class TestDataQuality:
    """Test data quality and completeness."""
    
    def test_no_empty_team_names(self, mock_fetch_html):
        """Test that team names are never empty strings."""
        matches = vlr.matches.upcoming(limit=10)
        
        for match in matches:
            assert match.team1.name != ""
            assert match.team2.name != ""
    
    def test_no_negative_scores(self, mock_fetch_html):
        """Test that scores are never negative."""
        matches = vlr.matches.completed(limit=10)
        
        for match in matches:
            if match.team1.score is not None:
                assert match.team1.score >= 0
            if match.team2.score is not None:
                assert match.team2.score >= 0
    
    def test_agent_stats_valid_ranges(self, mock_fetch_html):
        """Test that agent stats are in valid ranges."""
        stats = vlr.players.agent_stats(player_id=457)
        
        for stat in stats:
            # Rating should be reasonable
            if stat.rating is not None:
                assert 0 <= stat.rating <= 5.0
            
            # K/D should be reasonable
            if stat.kd is not None:
                assert 0 <= stat.kd <= 10.0
            
            # KAST should be between 0 and 1
            if stat.kast is not None:
                assert 0 <= stat.kast <= 1.0
            
            # Usage percent should be between 0 and 1
            if stat.usage_percent is not None:
                assert 0 <= stat.usage_percent <= 1.0
    
    def test_match_status_valid(self, mock_fetch_html):
        """Test that match status is always valid."""
        upcoming = vlr.matches.upcoming(limit=5)
        completed = vlr.matches.completed(limit=5)
        live = vlr.matches.live()
        
        all_matches = upcoming + completed + live
        valid_statuses = ["upcoming", "live", "completed"]
        
        for match in all_matches:
            assert match.status in valid_statuses


class TestEdgeCasesWithRealData:
    """Test edge cases using real data."""
    
    def test_handles_missing_optional_fields(self, mock_fetch_html):
        """Test that missing optional fields are handled gracefully."""
        profile = vlr.players.profile(player_id=457)
        
        if profile:
            # These fields might be None, should not crash
            _ = profile.avatar_url
            _ = profile.real_name
            
            # Lists should never be None, but can be empty
            assert isinstance(profile.socials, list)
            assert isinstance(profile.current_teams, list)
            assert isinstance(profile.past_teams, list)
    
    def test_handles_special_characters(self, mock_fetch_html):
        """Test that special characters in names are handled."""
        matches = vlr.matches.upcoming(limit=10)
        
        for match in matches:
            # Should handle team names with special characters
            assert isinstance(match.team1.name, str)
            assert isinstance(match.team2.name, str)
    
    def test_date_fields_valid_or_none(self, mock_fetch_html):
        """Test that date fields are valid dates or None."""
        matches = vlr.matches.upcoming(limit=5)
        
        for match in matches:
            if match.date is not None:
                # Should be a valid date object
                assert hasattr(match.date, 'year')
                assert hasattr(match.date, 'month')
                assert hasattr(match.date, 'day')
                # Year should be reasonable
                assert 2020 <= match.date.year <= 2030
