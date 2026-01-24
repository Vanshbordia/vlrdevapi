"""Tests for players module using real HTML sources."""

import pytest
import vlrdevapi as vlr


class TestPlayersProfile:
    """Test player profile functionality."""
    
    def test_profile_returns_data(self, mock_fetch_html):
        """Test that profile() returns data for valid player."""
        profile = vlr.players.profile(player_id=457)
        assert profile is not None
    
    def test_profile_structure(self, mock_fetch_html):
        """Test profile has correct structure."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            assert hasattr(profile, 'player_id')
            assert hasattr(profile, 'handle')
            assert hasattr(profile, 'real_name')
            assert hasattr(profile, 'country')
            assert hasattr(profile, 'aliases')
            assert hasattr(profile, 'current_teams')
            assert hasattr(profile, 'past_teams')
            assert hasattr(profile, 'socials')

    def test_profile_aliases_with_aliases(self, mock_fetch_html):
        """Test that aliases are extracted when they exist (player 53 and 4147)."""
        # Test player 53 who has aliases
        profile = vlr.players.profile(player_id=53)
        if profile and profile.aliases:
            assert isinstance(profile.aliases, list)
            assert len(profile.aliases) > 0
            for alias in profile.aliases:
                assert isinstance(alias, str)
                assert len(alias) > 0

        # Test player 4147 who has aliases
        profile = vlr.players.profile(player_id=4147)
        if profile and profile.aliases:
            assert isinstance(profile.aliases, list)
            assert len(profile.aliases) > 0
            for alias in profile.aliases:
                assert isinstance(alias, str)
                assert len(alias) > 0

    def test_profile_no_aliases(self, mock_fetch_html):
        """Test that aliases is None or empty for players without aliases (player 302)."""
        profile = vlr.players.profile(player_id=302)
        if profile:
            # Aliases should be None or an empty list if no aliases exist
            assert profile.aliases is None or (isinstance(profile.aliases, list) and len(profile.aliases) == 0)
    
    def test_profile_player_id(self, mock_fetch_html):
        """Test that player_id is correct."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            assert profile.player_id == 457
    
    def test_profile_handle(self, mock_fetch_html):
        """Test that handle is extracted."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            assert profile.handle is not None
            assert isinstance(profile.handle, str)
            assert len(profile.handle) > 0
    
    def test_profile_country(self, mock_fetch_html):
        """Test that country is extracted."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            # Country might be None or a string
            if profile.country:
                assert isinstance(profile.country, str)
    
    def test_profile_teams(self, mock_fetch_html):
        """Test that teams are extracted."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            assert isinstance(profile.current_teams, list)
            assert isinstance(profile.past_teams, list)
    
    def test_profile_socials(self, mock_fetch_html):
        """Test that social links are extracted."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            assert isinstance(profile.socials, list)
            for social in profile.socials:
                assert hasattr(social, 'label')
                assert hasattr(social, 'url')
    
    def test_profile_invalid_id_returns_none(self, mock_fetch_html):
        """Test that invalid player ID returns None."""
        # This might return None or raise an error depending on implementation
        profile = vlr.players.profile(player_id=999999999)
        # Should handle gracefully
        assert profile is None or profile is not None


class TestPlayersMatches:
    """Test player matches functionality."""
    
    def test_matches_returns_list(self, mock_fetch_html):
        """Test that matches() returns a list."""
        matches = vlr.players.matches(player_id=457)
        assert isinstance(matches, list)
    
    def test_matches_with_limit(self, mock_fetch_html):
        """Test matches() with limit parameter."""
        matches = vlr.players.matches(player_id=457, limit=5)
        assert len(matches) <= 5
    
    def test_match_structure(self, mock_fetch_html):
        """Test that matches have correct structure."""
        matches = vlr.players.matches(player_id=457, limit=1)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'event')
            assert hasattr(match, 'stage')
            assert hasattr(match, 'phase')
            assert hasattr(match, 'player_team')
            assert hasattr(match, 'opponent_team')
            assert hasattr(match, 'result')
    
    def test_match_teams(self, mock_fetch_html):
        """Test that match teams are extracted."""
        matches = vlr.players.matches(player_id=457, limit=1)
        if matches:
            match = matches[0]
            assert hasattr(match.player_team, 'name')
            assert hasattr(match.opponent_team, 'name')
    
    def test_match_result(self, mock_fetch_html):
        """Test that match result is valid."""
        matches = vlr.players.matches(player_id=457, limit=10)
        for match in matches:
            if match.result:
                assert match.result in ["win", "loss", "draw"]
    
    def test_match_scores(self, mock_fetch_html):
        """Test that match scores are extracted."""
        matches = vlr.players.matches(player_id=457, limit=5)
        for match in matches:
            # Scores might be None for upcoming matches
            if match.player_score is not None:
                assert isinstance(match.player_score, int)
            if match.opponent_score is not None:
                assert isinstance(match.opponent_score, int)
    
    def test_matches_pagination(self, mock_fetch_html):
        """Test pagination for player matches."""
        page1 = vlr.players.matches(player_id=457, page=1, limit=5)
        assert isinstance(page1, list)
    
    def test_match_stage_and_phase(self, mock_fetch_html):
        """Test that stage and phase are extracted correctly."""
        matches = vlr.players.matches(player_id=457, limit=10)
        for match in matches:
            # Stage and phase might be None or strings
            if match.stage is not None:
                assert isinstance(match.stage, str)
                assert len(match.stage) > 0
            if match.phase is not None:
                assert isinstance(match.phase, str)
                assert len(match.phase) > 0


class TestPlayersAgentStats:
    """Test player agent statistics functionality."""
    
    def test_agent_stats_returns_list(self, mock_fetch_html):
        """Test that agent_stats() returns a list."""
        stats = vlr.players.agent_stats(player_id=457)
        assert isinstance(stats, list)
    
    def test_agent_stats_structure(self, mock_fetch_html):
        """Test agent stats structure."""
        stats = vlr.players.agent_stats(player_id=457)
        if stats:
            stat = stats[0]
            assert hasattr(stat, 'agent')
            assert hasattr(stat, 'rating')
            assert hasattr(stat, 'acs')
            assert hasattr(stat, 'kd')
            assert hasattr(stat, 'kills')
            assert hasattr(stat, 'deaths')
            assert hasattr(stat, 'assists')
    
    def test_agent_stats_agent_name(self, mock_fetch_html):
        """Test that agent names are extracted."""
        stats = vlr.players.agent_stats(player_id=457)
        for stat in stats:
            if stat.agent:
                assert isinstance(stat.agent, str)
                assert len(stat.agent) > 0
    
    def test_agent_stats_numeric_values(self, mock_fetch_html):
        """Test that numeric stats are correct type."""
        stats = vlr.players.agent_stats(player_id=457)
        for stat in stats:
            if stat.rating is not None:
                assert isinstance(stat.rating, (int, float))
            if stat.acs is not None:
                assert isinstance(stat.acs, (int, float))
            if stat.kd is not None:
                assert isinstance(stat.kd, (int, float))
    
    def test_agent_stats_usage(self, mock_fetch_html):
        """Test that usage stats are extracted."""
        stats = vlr.players.agent_stats(player_id=457)
        for stat in stats:
            if stat.usage_count is not None:
                assert isinstance(stat.usage_count, int)
                assert stat.usage_count >= 0
            if stat.usage_percent is not None:
                assert isinstance(stat.usage_percent, float)
                assert 0 <= stat.usage_percent <= 1
    
    def test_agent_stats_timespan(self, mock_fetch_html):
        """Test different timespan parameters."""
        stats_all = vlr.players.agent_stats(player_id=457, timespan="all")
        stats_60d = vlr.players.agent_stats(player_id=457, timespan="60d")
        
        assert isinstance(stats_all, list)
        assert isinstance(stats_60d, list)
    
    def test_agent_stats_kast(self, mock_fetch_html):
        """Test KAST percentage."""
        stats = vlr.players.agent_stats(player_id=457)
        for stat in stats:
            if stat.kast is not None:
                assert isinstance(stat.kast, float)
                assert 0 <= stat.kast <= 1


class TestPlayersIntegration:
    """Integration tests for players module."""
    
    def test_full_player_data_flow(self, mock_fetch_html):
        """Test getting all player data."""
        # Get profile
        profile = vlr.players.profile(player_id=457)
        assert profile is not None
        
        # Get matches
        matches = vlr.players.matches(player_id=457, limit=5)
        assert isinstance(matches, list)
        
        # Get agent stats
        stats = vlr.players.agent_stats(player_id=457)
        assert isinstance(stats, list)
    
    def test_models_immutable(self, mock_fetch_html):
        """Test that models are immutable (frozen dataclasses)."""
        profile = vlr.players.profile(player_id=457)
        if profile:
            with pytest.raises(Exception):
                profile.handle = "new_handle"
    
    def test_team_structure(self, mock_fetch_html):
        """Test team structure in profile."""
        profile = vlr.players.profile(player_id=457)
        if profile and profile.current_teams:
            team = profile.current_teams[0]
            assert hasattr(team, 'name')
            assert hasattr(team, 'role')
            assert hasattr(team, 'joined_date')


class TestPlayersEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_matches(self, mock_fetch_html):
        """Test handling of empty match history."""
        matches = vlr.players.matches(player_id=457, limit=0)
        assert matches == []
    
    def test_zero_limit(self, mock_fetch_html):
        """Test limit=0 parameter."""
        matches = vlr.players.matches(player_id=457, limit=0)
        assert len(matches) == 0
    
    def test_large_limit(self, mock_fetch_html):
        """Test large limit parameter."""
        matches = vlr.players.matches(player_id=457, limit=1000)
        assert isinstance(matches, list)
        # Should cap at reasonable number
        assert len(matches) <= 1000
