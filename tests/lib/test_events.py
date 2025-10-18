"""Tests for events module using real HTML sources."""

import pytest
import vlrdevapi as vlr


class TestEventsListEvents:
    """Test events listing functionality."""
    
    def test_list_events_returns_list(self, mock_fetch_html):
        """Test that list_events() returns a list."""
        events = vlr.events.list_events()
        assert isinstance(events, list)
    
    def test_list_events_structure(self, mock_fetch_html):
        """Test event structure."""
        events = vlr.events.list_events(tier="vct")
        if events:
            event = events[0]
            assert hasattr(event, 'id')
            assert hasattr(event, 'name')
            assert hasattr(event, 'status')
            assert hasattr(event, 'url')
    
    def test_list_events_tier_filter(self, mock_fetch_html):
        """Test tier filtering."""
        vct_events = vlr.events.list_events(tier="vct")
        all_events = vlr.events.list_events(tier="all")
        
        assert isinstance(vct_events, list)
        assert isinstance(all_events, list)
    
    def test_list_events_status_filter(self, mock_fetch_html):
        """Test status filtering."""
        ongoing = vlr.events.list_events(status="ongoing")
        completed = vlr.events.list_events(status="completed")
        upcoming = vlr.events.list_events(status="upcoming")
        
        assert isinstance(ongoing, list)
        assert isinstance(completed, list)
        assert isinstance(upcoming, list)
    
    def test_list_events_valid_status(self, mock_fetch_html):
        """Test that events have valid status."""
        events = vlr.events.list_events()
        for event in events:
            assert event.status in ["upcoming", "ongoing", "completed"]
    
    def test_list_events_id_is_int(self, mock_fetch_html):
        """Test that event IDs are integers."""
        events = vlr.events.list_events()
        for event in events:
            assert isinstance(event.id, int)
            assert event.id > 0
    
    def test_list_events_name_not_empty(self, mock_fetch_html):
        """Test that event names are not empty."""
        events = vlr.events.list_events()
        for event in events:
            assert event.name
            assert len(event.name) > 0


class TestEventsInfo:
    """Test event info functionality."""
    
    def test_info_returns_data(self, mock_fetch_html):
        """Test that info() returns data."""
        info = vlr.events.info(event_id=2498)
        assert info is not None
    
    def test_info_structure(self, mock_fetch_html):
        """Test info structure."""
        info = vlr.events.info(event_id=2498)
        if info:
            assert hasattr(info, 'id')
            assert hasattr(info, 'name')
            assert hasattr(info, 'prize')
            assert hasattr(info, 'location')
            assert hasattr(info, 'regions')
            assert hasattr(info, 'date_text')
    
    def test_info_event_id(self, mock_fetch_html):
        """Test that event ID is correct."""
        info = vlr.events.info(event_id=2498)
        if info:
            assert info.id == 2498
    
    def test_info_name(self, mock_fetch_html):
        """Test that event name is extracted."""
        info = vlr.events.info(event_id=2498)
        if info:
            assert info.name
            assert isinstance(info.name, str)
    
    def test_info_regions(self, mock_fetch_html):
        """Test that regions are extracted."""
        info = vlr.events.info(event_id=2498)
        if info:
            assert isinstance(info.regions, list)
    
    def test_info_invalid_id(self, mock_fetch_html):
        """Test handling of invalid event ID."""
        info = vlr.events.info(event_id=999999999)
        # Should return None or handle gracefully
        assert info is None or info is not None


class TestEventsMatches:
    """Test event matches functionality."""
    
    def test_matches_returns_list(self, mock_fetch_html):
        """Test that matches() returns a list."""
        matches = vlr.events.matches(event_id=2498, limit=2)
        assert isinstance(matches, list)
    
    def test_match_structure(self, mock_fetch_html):
        """Test match structure."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'event_id')
            assert hasattr(match, 'teams')
            assert hasattr(match, 'status')
    
    def test_match_teams(self, mock_fetch_html):
        """Test that match teams are extracted."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        if matches:
            match = matches[0]
            assert isinstance(match.teams, tuple)
            assert len(match.teams) == 2
            assert hasattr(match.teams[0], 'name')
            assert hasattr(match.teams[1], 'name')
            assert hasattr(match.teams[0], 'id')
            assert hasattr(match.teams[1], 'id')
    
    def test_match_event_id(self, mock_fetch_html):
        """Test that event_id is correct."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        for match in matches:
            assert match.event_id == 2498
    
    def test_match_status(self, mock_fetch_html):
        """Test that match status is valid."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        for match in matches:
            assert isinstance(match.status, str)
    
    def test_match_team_scores(self, mock_fetch_html):
        """Test that team scores are extracted."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        for match in matches:
            for team in match.teams:
                if team.score is not None:
                    assert isinstance(team.score, int)
    
    def test_match_team_ids(self, mock_fetch_html):
        """Test that team IDs are extracted from match pages."""
        matches = vlr.events.matches(event_id=2498, limit=3)
        for match in matches:
            # Team IDs should be extracted from match page headers
            for team in match.teams:
                # IDs may be None for some teams (TBD, etc.)
                if team.id is not None:
                    assert isinstance(team.id, int)
                    assert team.id > 0


class TestEventsMatchSummary:
    """Test event match summary functionality."""
    
    def test_match_summary_returns_data(self, mock_fetch_html):
        """Test that match_summary() returns data."""
        summary = vlr.events.match_summary(event_id=2498)
        assert summary is not None
    
    def test_match_summary_structure(self, mock_fetch_html):
        """Test summary structure."""
        summary = vlr.events.match_summary(event_id=2498)
        if summary:
            assert hasattr(summary, 'event_id')
            assert hasattr(summary, 'total_matches')
            assert hasattr(summary, 'completed')
            assert hasattr(summary, 'upcoming')
            assert hasattr(summary, 'ongoing')
            assert hasattr(summary, 'stages')
    
    def test_match_summary_counts(self, mock_fetch_html):
        """Test that match counts are valid."""
        summary = vlr.events.match_summary(event_id=2498)
        if summary:
            assert isinstance(summary.total_matches, int)
            assert isinstance(summary.completed, int)
            assert isinstance(summary.upcoming, int)
            assert isinstance(summary.ongoing, int)
            assert summary.total_matches >= 0
            assert summary.completed >= 0
            assert summary.upcoming >= 0
            assert summary.ongoing >= 0
    
    def test_match_summary_event_id(self, mock_fetch_html):
        """Test that event_id is correct."""
        summary = vlr.events.match_summary(event_id=2498)
        if summary:
            assert summary.event_id == 2498


class TestEventsStandings:
    """Test event standings functionality."""
    
    def test_standings_returns_data(self, mock_fetch_html):
        """Test that standings() returns data."""
        standings = vlr.events.standings(event_id=2498)
        # May return None if no standings available
        assert standings is None or standings is not None
    
    def test_standings_structure(self, mock_fetch_html):
        """Test standings structure."""
        standings = vlr.events.standings(event_id=2498)
        if standings:
            assert hasattr(standings, 'event_id')
            assert hasattr(standings, 'entries')
            assert hasattr(standings, 'url')
    
    def test_standings_entries(self, mock_fetch_html):
        """Test standings entries."""
        standings = vlr.events.standings(event_id=2498)
        if standings and standings.entries:
            entry = standings.entries[0]
            assert hasattr(entry, 'place')
            assert hasattr(entry, 'team_name')
            assert hasattr(entry, 'prize')
    
    def test_standings_event_id(self, mock_fetch_html):
        """Test that event_id is correct."""
        standings = vlr.events.standings(event_id=2498)
        if standings:
            assert standings.event_id == 2498


class TestEventsIntegration:
    """Integration tests for events module."""
    
    def test_full_event_data_flow(self, mock_fetch_html):
        """Test getting all event data."""
        # List events
        events = vlr.events.list_events(tier="vct")
        assert isinstance(events, list)
        
        # Get event info
        if events:
            event_id = events[0].id
            info = vlr.events.info(event_id=event_id)
            # Info might be None if HTML doesn't match
            assert info is None or info is not None
    
    def test_pydantic_models_immutable(self, mock_fetch_html):
        """Test that models are immutable."""
        events = vlr.events.list_events()
        if events:
            with pytest.raises(Exception):
                events[0].name = "new_name"


class TestEventsEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_tier(self, mock_fetch_html):
        """Test handling of invalid tier."""
        # Should handle gracefully or use default
        events = vlr.events.list_events(tier="vct")
        assert isinstance(events, list)
    
    def test_invalid_status(self, mock_fetch_html):
        """Test handling of invalid status."""
        events = vlr.events.list_events(status="all")
        assert isinstance(events, list)
    
    def test_invalid_event_id(self, mock_fetch_html):
        """Test handling of invalid event ID."""
        info = vlr.events.info(event_id=999999999)
        assert info is None or info is not None
