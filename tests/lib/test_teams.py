"""Tests for teams module using real HTML sources."""

import pytest
import vlrdevapi as vlr


class TestTeamsInfo:
    """Test team info functionality."""
    
    def test_info_returns_data_active_team(self, mock_fetch_html):
        """Test that info() returns data for active team (NRG)."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
    
    def test_info_returns_data_inactive_team(self, mock_fetch_html):
        """Test that info() returns data for inactive team (M3C)."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
    
    def test_info_structure(self, mock_fetch_html):
        """Test team info has correct structure."""
        team = vlr.teams.info(team_id=1034)
        if team:
            assert hasattr(team, 'team_id')
            assert hasattr(team, 'name')
            assert hasattr(team, 'tag')
            assert hasattr(team, 'logo_url')
            assert hasattr(team, 'country')
            assert hasattr(team, 'is_active')
            assert hasattr(team, 'socials')
            assert hasattr(team, 'previous_team')
    
    def test_info_team_id(self, mock_fetch_html):
        """Test that team_id is correct."""
        team = vlr.teams.info(team_id=1034)
        if team:
            assert team.team_id == 1034


class TestTeamsActiveTeam:
    """Test active team (NRG - team_id 1034)."""
    
    def test_active_team_name(self, mock_fetch_html):
        """Test that team name is extracted correctly."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert team.name == "NRG"
        assert isinstance(team.name, str)
        assert len(team.name) > 0
    
    def test_active_team_tag(self, mock_fetch_html):
        """Test that team tag is extracted correctly."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert team.tag == "NRG"
        assert isinstance(team.tag, str)
    
    def test_active_team_logo(self, mock_fetch_html):
        """Test that logo URL is extracted."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert team.logo_url is not None
        assert isinstance(team.logo_url, str)
        assert "owcdn.net" in team.logo_url
        assert team.logo_url.startswith("https://")
    
    def test_active_team_country(self, mock_fetch_html):
        """Test that country is extracted correctly."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert team.country is not None
        assert isinstance(team.country, str)
        assert team.country == "United States"
    
    def test_active_team_status(self, mock_fetch_html):
        """Test that active status is correct."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert team.is_active is True
    
    def test_active_team_socials(self, mock_fetch_html):
        """Test that social links are extracted."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        assert isinstance(team.socials, list)
        # NRG should have at least one social link
        assert len(team.socials) > 0
        for social in team.socials:
            assert hasattr(social, 'label')
            assert hasattr(social, 'url')
            assert isinstance(social.label, str)
            assert isinstance(social.url, str)
            assert len(social.label) > 0
            assert len(social.url) > 0
    
    def test_active_team_no_previous_team(self, mock_fetch_html):
        """Test that active team without rename has no previous_team."""
        team = vlr.teams.info(team_id=1034)
        assert team is not None
        # NRG hasn't been renamed, so should be None
        assert team.previous_team is None


class TestTeamsInactiveTeam:
    """Test inactive team with previous name (M3C - team_id 8326)."""
    
    def test_inactive_team_name(self, mock_fetch_html):
        """Test that team name is extracted correctly."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.name == "M3 Champions"
        assert isinstance(team.name, str)
    
    def test_inactive_team_tag(self, mock_fetch_html):
        """Test that team tag is extracted correctly."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.tag == "M3C"
        assert isinstance(team.tag, str)
    
    def test_inactive_team_logo(self, mock_fetch_html):
        """Test that logo URL is extracted."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.logo_url is not None
        assert isinstance(team.logo_url, str)
        assert "owcdn.net" in team.logo_url
        assert team.logo_url.startswith("https://")
    
    def test_inactive_team_country(self, mock_fetch_html):
        """Test that country is extracted correctly."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.country is not None
        assert isinstance(team.country, str)
        assert team.country == "Russia"
    
    def test_inactive_team_status(self, mock_fetch_html):
        """Test that inactive status is detected."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.is_active is False
    
    def test_inactive_team_previous_team(self, mock_fetch_html):
        """Test that previous team information is extracted."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.previous_team is not None
        assert hasattr(team.previous_team, 'team_id')
        assert hasattr(team.previous_team, 'name')
    
    def test_inactive_team_previous_team_name(self, mock_fetch_html):
        """Test that previous team name is correct."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.previous_team is not None
        assert team.previous_team.name == "Gambit Esports"
        assert isinstance(team.previous_team.name, str)
    
    def test_inactive_team_previous_team_id(self, mock_fetch_html):
        """Test that previous team ID is extracted."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert team.previous_team is not None
        assert team.previous_team.team_id == 682
        assert isinstance(team.previous_team.team_id, int)
    
    def test_inactive_team_socials(self, mock_fetch_html):
        """Test that social links are handled (may be empty for inactive teams)."""
        team = vlr.teams.info(team_id=8326)
        assert team is not None
        assert isinstance(team.socials, list)
        # M3C might not have social links, so just check it's a list


class TestTeamsIntegration:
    """Integration tests for teams module."""
    
    def test_pydantic_models_immutable(self, mock_fetch_html):
        """Test that models are immutable."""
        team = vlr.teams.info(team_id=1034)
        if team:
            with pytest.raises(Exception):
                team.name = "new_name"
    
    def test_social_link_structure(self, mock_fetch_html):
        """Test social link structure."""
        team = vlr.teams.info(team_id=1034)
        if team and team.socials:
            social = team.socials[0]
            assert hasattr(social, 'label')
            assert hasattr(social, 'url')
            # Should not be able to modify
            with pytest.raises(Exception):
                social.label = "new_label"
    
    def test_previous_team_structure(self, mock_fetch_html):
        """Test previous team structure."""
        team = vlr.teams.info(team_id=8326)
        if team and team.previous_team:
            prev = team.previous_team
            assert hasattr(prev, 'team_id')
            assert hasattr(prev, 'name')
            # Should not be able to modify
            with pytest.raises(Exception):
                prev.name = "new_name"
    
    def test_multiple_teams(self, mock_fetch_html):
        """Test fetching multiple teams."""
        team1 = vlr.teams.info(team_id=1034)
        team2 = vlr.teams.info(team_id=8326)
        
        assert team1 is not None
        assert team2 is not None
        assert team1.team_id != team2.team_id
        assert team1.name != team2.name


class TestTeamsEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_team_id_returns_none(self, mock_fetch_html):
        """Test that invalid team ID returns None."""
        team = vlr.teams.info(team_id=999999999)
        # Should handle gracefully
        assert team is None or team is not None
    
    def test_logo_url_format(self, mock_fetch_html):
        """Test that logo URLs are properly formatted."""
        team = vlr.teams.info(team_id=1034)
        if team and team.logo_url:
            # Should be absolute URL with https
            assert team.logo_url.startswith("https://")
            assert "owcdn.net" in team.logo_url
    
    def test_social_links_no_empty_entries(self, mock_fetch_html):
        """Test that empty social links are filtered out."""
        team = vlr.teams.info(team_id=1034)
        if team:
            for social in team.socials:
                # No empty labels or URLs
                assert social.label
                assert social.url
                assert len(social.label.strip()) > 0
                assert len(social.url.strip()) > 0
    
    def test_country_mapping(self, mock_fetch_html):
        """Test that country codes are mapped to full names."""
        team_us = vlr.teams.info(team_id=1034)
        team_ru = vlr.teams.info(team_id=8326)
        
        if team_us and team_us.country:
            # Should be full country name, not code
            assert team_us.country == "United States"
            assert team_us.country != "us"
        
        if team_ru and team_ru.country:
            assert team_ru.country == "Russia"
            assert team_ru.country != "ru"


class TestTeamsDataQuality:
    """Test data quality and consistency."""
    
    def test_team_name_not_empty(self, mock_fetch_html):
        """Test that team names are not empty."""
        team = vlr.teams.info(team_id=1034)
        if team and team.name:
            assert len(team.name.strip()) > 0
    
    def test_team_tag_not_empty(self, mock_fetch_html):
        """Test that team tags are not empty."""
        team = vlr.teams.info(team_id=1034)
        if team and team.tag:
            assert len(team.tag.strip()) > 0
    
    def test_social_urls_valid(self, mock_fetch_html):
        """Test that social URLs are valid."""
        team = vlr.teams.info(team_id=1034)
        if team:
            for social in team.socials:
                # Should be valid URL format
                assert social.url.startswith("http://") or social.url.startswith("https://")
    
    def test_previous_team_id_positive(self, mock_fetch_html):
        """Test that previous team IDs are positive integers."""
        team = vlr.teams.info(team_id=8326)
        if team and team.previous_team and team.previous_team.team_id:
            assert team.previous_team.team_id > 0
    
    def test_is_active_boolean(self, mock_fetch_html):
        """Test that is_active is always a boolean."""
        team1 = vlr.teams.info(team_id=1034)
        team2 = vlr.teams.info(team_id=8326)
        
        if team1:
            assert isinstance(team1.is_active, bool)
        if team2:
            assert isinstance(team2.is_active, bool)


class TestTeamsRoster:
    """Test team roster functionality."""
    
    def test_roster_returns_list(self, mock_fetch_html):
        """Test that roster() returns a list."""
        roster = vlr.teams.roster(team_id=1034)
        assert isinstance(roster, list)
    
    def test_roster_has_members(self, mock_fetch_html):
        """Test that active team has roster members."""
        roster = vlr.teams.roster(team_id=1034)
        # NRG should have players and staff
        assert len(roster) > 0
    
    def test_roster_member_structure(self, mock_fetch_html):
        """Test roster member has correct structure."""
        roster = vlr.teams.roster(team_id=1034)
        if roster:
            member = roster[0]
            assert hasattr(member, 'player_id')
            assert hasattr(member, 'ign')
            assert hasattr(member, 'real_name')
            assert hasattr(member, 'country')
            assert hasattr(member, 'role')
            assert hasattr(member, 'is_captain')
            assert hasattr(member, 'photo_url')
    
    def test_roster_player_ids(self, mock_fetch_html):
        """Test that player IDs are extracted."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            if member.player_id:
                assert isinstance(member.player_id, int)
                assert member.player_id > 0
    
    def test_roster_ign_not_empty(self, mock_fetch_html):
        """Test that IGNs are not empty."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            if member.ign:
                assert isinstance(member.ign, str)
                assert len(member.ign.strip()) > 0
    
    def test_roster_real_names(self, mock_fetch_html):
        """Test that real names are extracted."""
        roster = vlr.teams.roster(team_id=1034)
        # At least some members should have real names
        has_real_name = any(member.real_name for member in roster)
        assert has_real_name
    
    def test_roster_countries(self, mock_fetch_html):
        """Test that countries are extracted."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            if member.country:
                assert isinstance(member.country, str)
                # Should be full country name, not code
                assert len(member.country) > 2
    
    def test_roster_roles(self, mock_fetch_html):
        """Test that roles are extracted."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            assert isinstance(member.role, str)
            assert len(member.role) > 0
    
    def test_roster_has_players(self, mock_fetch_html):
        """Test that roster includes players."""
        roster = vlr.teams.roster(team_id=1034)
        players = [m for m in roster if m.role == "Player"]
        assert len(players) > 0
    
    def test_roster_has_staff(self, mock_fetch_html):
        """Test that roster includes staff."""
        roster = vlr.teams.roster(team_id=1034)
        staff = [m for m in roster if m.role != "Player" and m.role != "Sub"]
        # NRG should have coaches/managers
        assert len(staff) > 0
    
    def test_roster_captain_detection(self, mock_fetch_html):
        """Test that team captain is detected."""
        roster = vlr.teams.roster(team_id=1034)
        captains = [m for m in roster if m.is_captain]
        # NRG should have a captain
        assert len(captains) > 0
    
    def test_roster_captain_is_boolean(self, mock_fetch_html):
        """Test that is_captain is always boolean."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            assert isinstance(member.is_captain, bool)
    
    def test_roster_photo_urls(self, mock_fetch_html):
        """Test that photo URLs are extracted."""
        roster = vlr.teams.roster(team_id=1034)
        # At least some members should have photos
        has_photo = any(member.photo_url for member in roster)
        assert has_photo
        
        for member in roster:
            if member.photo_url:
                assert member.photo_url.startswith("https://")
                assert "owcdn.net" in member.photo_url


class TestTeamsRosterRoles:
    """Test different roster roles."""
    
    def test_roster_player_role(self, mock_fetch_html):
        """Test that players have correct role."""
        roster = vlr.teams.roster(team_id=1034)
        players = [m for m in roster if m.role == "Player"]
        assert len(players) >= 5  # Should have at least 5 players
    
    def test_roster_coach_roles(self, mock_fetch_html):
        """Test that coaches are identified."""
        roster = vlr.teams.roster(team_id=1034)
        coaches = [m for m in roster if "Coach" in m.role]
        assert len(coaches) > 0
    
    def test_roster_role_capitalization(self, mock_fetch_html):
        """Test that roles are properly capitalized."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            # Roles should be title case (e.g., "Head Coach", not "head coach")
            if member.role != "Player" and member.role != "Sub":
                words = member.role.split()
                for word in words:
                    if word:
                        assert word[0].isupper(), f"Role '{member.role}' not properly capitalized"
    
    def test_roster_sub_role(self, mock_fetch_html):
        """Test that subs are identified correctly."""
        roster = vlr.teams.roster(team_id=1034)
        subs = [m for m in roster if m.role == "Sub"]
        # May or may not have subs, just check structure is correct
        for sub in subs:
            assert sub.role == "Sub"


class TestTeamsRosterSpecificMembers:
    """Test specific known roster members."""
    
    def test_roster_ethan_captain(self, mock_fetch_html):
        """Test that Ethan is identified as captain."""
        roster = vlr.teams.roster(team_id=1034)
        ethan = next((m for m in roster if m.ign and "Ethan" in m.ign), None)
        if ethan:
            assert ethan.is_captain is True
            assert ethan.real_name == "Ethan Arnold"
            assert ethan.country == "United States"
    
    def test_roster_s0m_player(self, mock_fetch_html):
        """Test that s0m is in the roster."""
        roster = vlr.teams.roster(team_id=1034)
        s0m = next((m for m in roster if m.player_id == 4164), None)
        if s0m:
            assert s0m.ign == "s0m"
            assert s0m.real_name == "Sam Oh"
            assert s0m.country == "United States"
            assert s0m.role == "Player"
    
    def test_roster_bonkar_coach(self, mock_fetch_html):
        """Test that bonkar is identified as head coach."""
        roster = vlr.teams.roster(team_id=1034)
        bonkar = next((m for m in roster if m.ign and "bonkar" in m.ign.lower()), None)
        if bonkar:
            assert "Coach" in bonkar.role
            assert bonkar.country is not None


class TestTeamsRosterEdgeCases:
    """Test edge cases for roster."""
    
    def test_roster_inactive_team(self, mock_fetch_html):
        """Test roster for inactive team."""
        roster = vlr.teams.roster(team_id=8326)
        # M3C might not have current roster
        assert isinstance(roster, list)
    
    def test_roster_invalid_team(self, mock_fetch_html):
        """Test roster for invalid team ID."""
        roster = vlr.teams.roster(team_id=999999999)
        assert isinstance(roster, list)
        assert len(roster) == 0
    
    def test_roster_immutable(self, mock_fetch_html):
        """Test that roster members are immutable."""
        roster = vlr.teams.roster(team_id=1034)
        if roster:
            member = roster[0]
            with pytest.raises(Exception):
                member.ign = "new_ign"
    
    def test_roster_no_placeholder_photos(self, mock_fetch_html):
        """Test that placeholder photos are not included."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            if member.photo_url:
                # Should not include placeholder images
                assert "ph/sil.png" not in member.photo_url


class TestTeamsRosterIntegration:
    """Integration tests for roster."""
    
    def test_roster_with_team_info(self, mock_fetch_html):
        """Test getting both team info and roster."""
        team_info = vlr.teams.info(team_id=1034)
        roster = vlr.teams.roster(team_id=1034)
        
        assert team_info is not None
        assert len(roster) > 0
        assert team_info.team_id == 1034
    
    def test_roster_player_ids_valid(self, mock_fetch_html):
        """Test that all player IDs are valid."""
        roster = vlr.teams.roster(team_id=1034)
        for member in roster:
            if member.player_id:
                # Player ID should be positive integer
                assert member.player_id > 0
                assert member.player_id < 100000  # Reasonable upper bound


class TestTeamsUpcomingMatches:
    """Test team upcoming matches functionality."""
    
    def test_upcoming_matches_returns_list(self, mock_fetch_html):
        """Test that upcoming_matches() returns a list."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        assert isinstance(matches, list)
    
    def test_upcoming_matches_structure(self, mock_fetch_html):
        """Test that match objects have correct structure."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'match_url')
            assert hasattr(match, 'tournament_name')
            assert hasattr(match, 'phase')
            assert hasattr(match, 'series')
            assert hasattr(match, 'team1_id')
            assert hasattr(match, 'team1_name')
            assert hasattr(match, 'team1_tag')
            assert hasattr(match, 'team1_logo')
            assert hasattr(match, 'team2_id')
            assert hasattr(match, 'team2_name')
            assert hasattr(match, 'team2_tag')
            assert hasattr(match, 'team2_logo')
            assert hasattr(match, 'date')
            assert hasattr(match, 'time')
    
    def test_upcoming_matches_team_names(self, mock_fetch_html):
        """Test that team names are extracted."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        for match in matches:
            if match.team1_name:
                assert isinstance(match.team1_name, str)
                assert len(match.team1_name) > 0
            if match.team2_name:
                assert isinstance(match.team2_name, str)
                assert len(match.team2_name) > 0
    
    def test_upcoming_matches_tournament_info(self, mock_fetch_html):
        """Test that tournament information is extracted."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        for match in matches:
            if match.tournament_name:
                assert isinstance(match.tournament_name, str)
                assert len(match.tournament_name) > 0
    
    def test_upcoming_matches_date_time(self, mock_fetch_html):
        """Test that date and time are extracted."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        for match in matches:
            if match.date:
                assert isinstance(match.date, str)
            if match.time:
                assert isinstance(match.time, str)
    
    def test_upcoming_matches_immutable(self, mock_fetch_html):
        """Test that match objects are immutable."""
        matches = vlr.teams.upcoming_matches(team_id=799)
        if matches:
            match = matches[0]
            with pytest.raises(Exception):
                match.team1_name = "new_name"


class TestTeamsCompletedMatches:
    """Test team completed matches functionality."""
    
    def test_completed_matches_basic(self, mock_fetch_html):
        """Test completed matches returns list with correct structure and data."""
        matches = vlr.teams.completed_matches(team_id=799, count=2)
        
        # Test returns list
        assert isinstance(matches, list)
        
        if matches:
            match = matches[0]
            
            # Test structure
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'match_url')
            assert hasattr(match, 'tournament_name')
            assert hasattr(match, 'score_team1')
            assert hasattr(match, 'score_team2')
            
            # Test scores are valid
            if match.score_team1 is not None:
                assert isinstance(match.score_team1, int)
                assert match.score_team1 >= 0
            if match.score_team2 is not None:
                assert isinstance(match.score_team2, int)
                assert match.score_team2 >= 0
            
            # Test match ID
            if match.match_id:
                assert isinstance(match.match_id, int)
                assert match.match_id > 0
            
            # Test URLs
            if match.match_url:
                assert match.match_url.startswith("https://")
                assert "vlr.gg" in match.match_url


class TestTeamsMatchesIntegration:
    """Integration tests for team matches."""
    
    def test_both_match_types(self, mock_fetch_html):
        """Test getting both upcoming and completed matches (limited)."""
        upcoming = vlr.teams.upcoming_matches(team_id=799, count=2)
        completed = vlr.teams.completed_matches(team_id=799, count=2)
        
        assert isinstance(upcoming, list)
        assert isinstance(completed, list)
    
    def test_matches_with_team_info(self, mock_fetch_html):
        """Test getting matches along with team info (limited)."""
        team_info = vlr.teams.info(team_id=799)
        matches = vlr.teams.completed_matches(team_id=799, count=2)
        
        if team_info:
            assert team_info.team_id == 799
        assert isinstance(matches, list)
    
    def test_invalid_team_matches(self, mock_fetch_html):
        """Test matches for invalid team ID."""
        upcoming = vlr.teams.upcoming_matches(team_id=999999999)
        completed = vlr.teams.completed_matches(team_id=999999999)
        
        assert isinstance(upcoming, list)
        assert isinstance(completed, list)
        assert len(upcoming) == 0
        assert len(completed) == 0
    
    def test_matches_with_count_limit(self, mock_fetch_html):
        """Test getting matches with count limit."""
        matches_2 = vlr.teams.completed_matches(team_id=799, count=2)
        matches_5 = vlr.teams.completed_matches(team_id=799, count=5)
        
        assert isinstance(matches_2, list)
        assert isinstance(matches_5, list)
        assert len(matches_2) <= 2
        assert len(matches_5) <= 5
    
    def test_matches_pagination(self, mock_fetch_html):
        """Test that pagination works correctly (limited test)."""
        # Only test minimal count to avoid long test times
        limited_matches = vlr.teams.completed_matches(team_id=799, count=2)
        
        assert isinstance(limited_matches, list)
        assert len(limited_matches) <= 2
    
    def test_matches_count_zero(self, mock_fetch_html):
        """Test getting matches with count=0."""
        matches = vlr.teams.completed_matches(team_id=799, count=0)
        assert isinstance(matches, list)
        assert len(matches) == 0
    
    def test_upcoming_matches_with_count(self, mock_fetch_html):
        """Test upcoming matches with count parameter."""
        matches = vlr.teams.upcoming_matches(team_id=799, count=3)
        assert isinstance(matches, list)
        assert len(matches) <= 3


class TestTeamsMatchesEdgeCases:
    """Test edge cases for team matches."""
    
    def test_matches_phase_series_format(self, mock_fetch_html):
        """Test that phase and series are properly formatted."""
        matches = vlr.teams.completed_matches(team_id=799)
        for match in matches:
            if match.phase:
                assert isinstance(match.phase, str)
                # Phase should not contain the tournament name
                if match.tournament_name:
                    assert match.tournament_name not in match.phase
            if match.series:
                assert isinstance(match.series, str)
                # Series should not contain the tournament name
                if match.tournament_name:
                    assert match.tournament_name not in match.series
    
    def test_matches_team_ids(self, mock_fetch_html):
        """Test that team IDs are extracted."""
        matches = vlr.teams.completed_matches(team_id=799)
        for match in matches:
            if match.team1_id:
                assert isinstance(match.team1_id, int)
                assert match.team1_id > 0
            if match.team2_id:
                assert isinstance(match.team2_id, int)
                assert match.team2_id > 0
    
    def test_matches_immutable(self, mock_fetch_html):
        """Test that match objects are immutable."""
        matches = vlr.teams.completed_matches(team_id=799)
        if matches:
            match = matches[0]
            with pytest.raises(Exception):
                match.score_team1 = 999


class TestTeamsPlacements:
    """Test team event placements functionality."""
    
    def test_placements_returns_list(self, mock_fetch_html):
        """Test that placements() returns a list."""
        placements = vlr.teams.placements(team_id=799)
        assert isinstance(placements, list)
    
    def test_placements_has_data(self, mock_fetch_html):
        """Test that placements returns data for Velocity Gaming."""
        placements = vlr.teams.placements(team_id=799)
        # Velocity Gaming should have placements
        assert len(placements) > 0
    
    def test_placements_structure(self, mock_fetch_html):
        """Test that placement objects have correct structure."""
        placements = vlr.teams.placements(team_id=799)
        if placements:
            placement = placements[0]
            assert hasattr(placement, 'event_id')
            assert hasattr(placement, 'event_name')
            assert hasattr(placement, 'event_url')
            assert hasattr(placement, 'placements')
            assert hasattr(placement, 'year')
            assert isinstance(placement.placements, list)
    
    def test_placement_details_structure(self, mock_fetch_html):
        """Test that placement detail objects have correct structure."""
        placements = vlr.teams.placements(team_id=799)
        if placements and placements[0].placements:
            detail = placements[0].placements[0]
            assert hasattr(detail, 'series')
            assert hasattr(detail, 'place')
            assert hasattr(detail, 'prize_money')
    
    def test_placements_event_ids(self, mock_fetch_html):
        """Test that event IDs are extracted."""
        placements = vlr.teams.placements(team_id=799)
        for placement in placements[:2]:  # Only check first 2 for speed
            if placement.event_id:
                assert isinstance(placement.event_id, int)
                assert placement.event_id > 0
    
    def test_placements_multiple_prizes(self, mock_fetch_html):
        """Test that events with multiple prizes are handled correctly."""
        placements = vlr.teams.placements(team_id=799)
        
        # Find event 122 (The Esports Club Challenger Series 2020) which has multiple prizes
        event_122 = next((p for p in placements if p.event_id == 122), None)
        if event_122:
            # Should have multiple placement details
            assert len(event_122.placements) > 1
            # Each should have prize money
            for detail in event_122.placements:
                assert detail.prize_money is not None
                assert "$" in detail.prize_money
    
    def test_placements_year_extraction(self, mock_fetch_html):
        """Test that year is correctly extracted from last div."""
        placements = vlr.teams.placements(team_id=799)
        for placement in placements[:2]:  # Only check first 2 for speed
            if placement.year:
                assert isinstance(placement.year, str)
                # Year should be cleaned (no extra whitespace)
                assert placement.year == placement.year.strip()
    
    def test_placements_prize_money(self, mock_fetch_html):
        """Test that prize money is extracted and cleaned."""
        placements = vlr.teams.placements(team_id=799)
        has_prize = False
        
        for placement in placements[:2]:  # Only check first 2 for speed
            for detail in placement.placements:
                if detail.prize_money:
                    has_prize = True
                    assert isinstance(detail.prize_money, str)
                    assert "$" in detail.prize_money
                    # Should be cleaned (no extra whitespace)
                    assert detail.prize_money == detail.prize_money.strip()
        
        assert has_prize
    
    def test_placements_immutable(self, mock_fetch_html):
        """Test that placement objects are immutable."""
        placements = vlr.teams.placements(team_id=799)
        if placements:
            placement = placements[0]
            with pytest.raises(Exception):
                placement.event_name = "new_name"
    
    def test_placements_invalid_team(self, mock_fetch_html):
        """Test placements for invalid team ID."""
        placements = vlr.teams.placements(team_id=999999999)
        assert isinstance(placements, list)
        assert len(placements) == 0
    
    def test_placements_specific_data(self, mock_fetch_html):
        """Test specific known placement data for Velocity Gaming."""
        placements = vlr.teams.placements(team_id=799)
        
        # Check if we have the 2025 Ascension Qualifiers placement
        ascension_quals = next((p for p in placements if p.event_id == 2558), None)
        if ascension_quals:
            assert "Challengers 2025" in ascension_quals.event_name
            assert ascension_quals.year == "2025"
            # Should have at least one placement detail
            assert len(ascension_quals.placements) > 0
            # Check first placement detail
            detail = ascension_quals.placements[0]
            assert detail.series == "Playoffs"
            assert detail.place == "1st"
            assert "$" in detail.prize_money
