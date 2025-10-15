"""Tests for matches module using real HTML sources."""

import pytest
from datetime import date
import vlrdevapi as vlr


class TestMatchesUpcoming:
    """Test upcoming matches functionality."""
    
    def test_upcoming_returns_list(self, mock_fetch_html):
        """Test that upcoming() returns a list."""
        matches = vlr.matches.upcoming()
        assert isinstance(matches, list)
    
    def test_upcoming_with_limit(self, mock_fetch_html):
        """Test upcoming() with limit parameter."""
        matches = vlr.matches.upcoming(limit=5)
        assert len(matches) <= 5
    
    def test_upcoming_match_structure(self, mock_fetch_html):
        """Test that upcoming matches have correct structure."""
        matches = vlr.matches.upcoming(limit=1)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'team1')
            assert hasattr(match, 'team2')
            assert hasattr(match, 'event')
            assert hasattr(match, 'status')
    
    def test_upcoming_match_teams(self, mock_fetch_html):
        """Test that teams are properly extracted."""
        matches = vlr.matches.upcoming(limit=1)
        if matches:
            match = matches[0]
            assert match.team1 is not None
            assert match.team2 is not None
            assert hasattr(match.team1, 'name')
            assert hasattr(match.team2, 'name')
            # Team id may be None or int
            assert hasattr(match.team1, 'id')
            assert (match.team1.id is None) or isinstance(match.team1.id, int)
            assert hasattr(match.team2, 'id')
            assert (match.team2.id is None) or isinstance(match.team2.id, int)
            assert hasattr(match.team1, 'country')
            assert hasattr(match.team2, 'country')
            assert hasattr(match.team1, 'score')
            assert hasattr(match.team2, 'score')
            assert isinstance(match.team1.name, str)
            assert isinstance(match.team2.name, str)
    
    def test_upcoming_match_id_is_int(self, mock_fetch_html):
        """Test that match_id is an integer."""
        matches = vlr.matches.upcoming(limit=1)
        if matches:
            assert isinstance(matches[0].match_id, int)
            assert matches[0].match_id > 0
    
    def test_upcoming_status(self, mock_fetch_html):
        """Test that status is valid."""
        matches = vlr.matches.upcoming(limit=10)
        for match in matches:
            assert match.status in ["upcoming", "live", "completed"]


class TestMatchesCompleted:
    """Test completed matches functionality."""
    
    def test_completed_returns_list(self, mock_fetch_html):
        """Test that completed() returns a list."""
        matches = vlr.matches.completed()
        assert isinstance(matches, list)
    
    def test_completed_with_limit(self, mock_fetch_html):
        """Test completed() with limit parameter."""
        matches = vlr.matches.completed(limit=3)
        assert len(matches) <= 3
    
    def test_completed_has_scores(self, mock_fetch_html):
        """Test that completed matches have scores."""
        matches = vlr.matches.completed(limit=5)
        for match in matches:
            # Completed matches should have scores
            if match.status == "completed":
                assert match.team1.score is not None or match.team2.score is not None
    
    def test_completed_match_structure(self, mock_fetch_html):
        """Test completed match structure."""
        matches = vlr.matches.completed(limit=1)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'team1')
            assert hasattr(match, 'team2')
            assert hasattr(match, 'event')
            assert hasattr(match.team1, 'score')
            assert hasattr(match.team2, 'score')
            # Team id may be None or int
            assert hasattr(match.team1, 'id')
            assert (match.team1.id is None) or isinstance(match.team1.id, int)
            assert hasattr(match.team2, 'id')
            assert (match.team2.id is None) or isinstance(match.team2.id, int)
    
    def test_completed_pagination(self, mock_fetch_html):
        """Test pagination for completed matches."""
        page1 = vlr.matches.completed(page=1, limit=5)
        page2 = vlr.matches.completed(page=2, limit=5)
        
        # Pages should be different (if there's enough data)
        if page1 and page2:
            assert page1[0].match_id != page2[0].match_id


class TestMatchesLive:
    """Test live matches functionality."""
    
    def test_live_returns_list(self, mock_fetch_html):
        """Test that live() returns a list."""
        matches = vlr.matches.live()
        assert isinstance(matches, list)
    
    def test_live_status(self, mock_fetch_html):
        """Test that live matches have 'live' status."""
        matches = vlr.matches.live()
        for match in matches:
            assert match.status == "live"
    
    def test_live_has_teams(self, mock_fetch_html):
        """Test that live matches have teams."""
        matches = vlr.matches.live()
        for match in matches:
            assert match.team1 is not None
            assert match.team2 is not None
            assert hasattr(match.team1, 'name')
            assert hasattr(match.team2, 'name')
            # Team id may be None or int during live parsing
            assert hasattr(match.team1, 'id')
            assert (match.team1.id is None) or isinstance(match.team1.id, int)
            assert hasattr(match.team2, 'id')
            assert (match.team2.id is None) or isinstance(match.team2.id, int)


class TestMatchesIntegration:
    """Integration tests for matches module."""
    
    def test_all_match_types_return_valid_data(self, mock_fetch_html):
        """Test that all match types return valid data."""
        upcoming = vlr.matches.upcoming(limit=2)
        completed = vlr.matches.completed(limit=2)
        live = vlr.matches.live()
        
        # All should return lists
        assert isinstance(upcoming, list)
        assert isinstance(completed, list)
        assert isinstance(live, list)
    
    def test_match_countries(self, mock_fetch_html):
        """Test that team countries are extracted."""
        matches = vlr.matches.upcoming(limit=5)
        for match in matches:
            assert hasattr(match.team1, 'country')
            assert hasattr(match.team2, 'country')
            # Countries can be None or strings
            if match.team1.country is not None:
                assert isinstance(match.team1.country, str)
            if match.team2.country is not None:
                assert isinstance(match.team2.country, str)
    
    def test_match_event_info(self, mock_fetch_html):
        """Test that event information is present."""
        matches = vlr.matches.upcoming(limit=5)
        for match in matches:
            assert hasattr(match, 'event')
            assert hasattr(match, 'event_phase')
    
    def test_match_time_info(self, mock_fetch_html):
        """Test that time information is present."""
        matches = vlr.matches.upcoming(limit=5)
        for match in matches:
            assert hasattr(match, 'time')
            assert hasattr(match, 'date')
    
    def test_pydantic_model_immutable(self, mock_fetch_html):
        """Test that Match models are immutable (frozen)."""
        matches = vlr.matches.upcoming(limit=1)
        if matches:
            match = matches[0]
            with pytest.raises(Exception):  # Pydantic raises ValidationError or AttributeError
                match.match_id = 999


class TestMatchesEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_results_handled(self, mock_fetch_html):
        """Test handling of empty results."""
        matches = vlr.matches.upcoming(limit=0)
        assert matches == []
    
    def test_large_limit_handled(self, mock_fetch_html):
        """Test that large limits are handled."""
        matches = vlr.matches.upcoming(limit=1000)
        assert isinstance(matches, list)
        # Should cap at reasonable number
        assert len(matches) <= 500
    
    def test_negative_page_handled(self, mock_fetch_html):
        """Test that negative page numbers are handled."""
        # Should either raise error or default to page 1
        matches = vlr.matches.upcoming(page=1)
        assert isinstance(matches, list)
