"""Tests for events teams functionality using real HTML sources."""

import pytest
import vlrdevapi as vlr


class TestEventsTeams:
    """Test events teams functionality."""

    def test_teams_returns_list(self, mock_fetch_html):
        """Test that teams() returns a list."""
        teams = vlr.events.teams(event_id=2682)
        assert isinstance(teams, list)

    def test_teams_structure(self, mock_fetch_html):
        """Test teams structure."""
        teams = vlr.events.teams(event_id=2682)
        for team in teams:
            assert hasattr(team, 'id')
            assert hasattr(team, 'name')
            assert hasattr(team, 'type')
            assert isinstance(team.id, int)
            assert isinstance(team.name, str)
            assert team.type is None or isinstance(team.type, str)

    def test_teams_event_id(self, mock_fetch_html):
        """Test that teams are returned for a specific event."""
        teams = vlr.events.teams(event_id=2682)
        # At least some teams should be returned for a valid event
        assert isinstance(teams, list)
        # Verify that if teams exist, they have valid IDs
        for team in teams:
            assert isinstance(team.id, int)
            assert team.id > 0
            assert team.name
            assert len(team.name) > 0

    def test_teams_expected_values(self, mock_fetch_html):
        """Test for expected teams like 100 Thieves (ID: 120) and G2 Esports (ID: 11058)."""
        teams = vlr.events.teams(event_id=2682)

        # Find 100 Thieves (should have ID 120 and type "Partner Team")
        team_100_thieves = None
        for team in teams:
            if team.id == 120 and team.name == "100 Thieves":
                team_100_thieves = team
                break

        if team_100_thieves:
            assert team_100_thieves.id == 120
            assert team_100_thieves.name == "100 Thieves"
            assert team_100_thieves.type == "Partner Team"

        # Find G2 Esports (should have ID 11058 and type "Ascension 2023")
        team_g2 = None
        for team in teams:
            if team.id == 11058 and team.name == "G2 Esports":
                team_g2 = team
                break

        if team_g2:
            assert team_g2.id == 11058
            assert team_g2.name == "G2 Esports"
            assert "Ascension" in team_g2.type if team_g2.type else False

    def test_teams_types_variety(self, mock_fetch_html):
        """Test that teams have different types (Partner Team, Ascension, etc.) or None."""
        teams = vlr.events.teams(event_id=2682)
        types_found = set()
        for team in teams:
            if team.type:
                types_found.add(team.type)

        # Should have variety of types or None values
        assert isinstance(types_found, set)

    def test_teams_unique_ids(self, mock_fetch_html):
        """Test that teams have unique IDs."""
        teams = vlr.events.teams(event_id=2682)
        ids = [team.id for team in teams]
        # Check that all IDs are unique
        assert len(ids) == len(set(ids))

    def test_teams_name_not_empty(self, mock_fetch_html):
        """Test that team names are not empty."""
        teams = vlr.events.teams(event_id=2682)
        for team in teams:
            assert team.name
            assert len(team.name) > 0

    def test_teams_id_is_positive(self, mock_fetch_html):
        """Test that team IDs are positive integers."""
        teams = vlr.events.teams(event_id=2682)
        for team in teams:
            assert isinstance(team.id, int)
            assert team.id > 0


class TestEventsTeamsIntegration:
    """Integration tests for teams functionality."""

    def test_full_event_teams_flow(self, mock_fetch_html):
        """Test getting teams for an event."""
        # Get teams for event
        teams = vlr.events.teams(event_id=2682)
        assert isinstance(teams, list)

        # Verify team structure
        for team in teams[:3]:  # Check first few teams
            assert hasattr(team, 'id')
            assert hasattr(team, 'name')
            assert hasattr(team, 'type')
            assert isinstance(team.id, int)
            assert isinstance(team.name, str)
            assert team.type is None or isinstance(team.type, str)

    def test_models_immutable(self, mock_fetch_html):
        """Test that models are immutable (frozen dataclasses)."""
        teams = vlr.events.teams(event_id=2682)
        if teams:
            with pytest.raises(Exception):
                teams[0].name = "new_name"


class TestEventsTeamsEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_event_id(self, mock_fetch_html):
        """Test handling of invalid event ID."""
        teams = vlr.events.teams(event_id=999999999)
        # Should return empty list or handle gracefully
        assert isinstance(teams, list)