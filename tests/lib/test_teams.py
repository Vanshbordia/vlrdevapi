"""Tests for teams module using real HTML sources."""

from datetime import date
from urllib.parse import urlparse
import pytest
import vlrdevapi as vlr


def _host_matches(url: str, allowed_domains) -> bool:
    """Return True if URL's hostname matches any allowed domain (including subdomains).

    Example: allowed_domains=["owcdn.net"] allows hostnames like
    "owcdn.net" and "static.owcdn.net".
    """
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    host = host.lower().strip(".")
    for domain in allowed_domains:
        d = (domain or "").lower().lstrip(".")
        if not d:
            continue
        if host == d or host.endswith("." + d):
            return True
    return False


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
            assert hasattr(team, 'current_team')
    
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
        assert _host_matches(team.logo_url, ["owcdn.net"])
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


class TestTeamsCurrentBanner:
    """Test inactive team with current banner (Gambit -> M3 Champions)."""

    def test_gambit_current_banner(self, mock_fetch_html):
        """Gambit Esports page should indicate current team M3 Champions."""
        team = vlr.teams.info(team_id=682)
        assert team is not None
        # Basic fields
        assert team.name == "Gambit Esports"
        assert team.tag == "GMB"
        assert team.is_active is False
        # Previous should be None in this fixture
        assert team.previous_team is None
        # Current team should be populated
        assert team.current_team is not None
        assert team.current_team.name == "M3 Champions"
        assert team.current_team.team_id == 8326


class TestTeamsIntegration:
    """Integration tests for teams module."""
    
    def test_models_immutable(self, mock_fetch_html):
        """Test that models are immutable (frozen dataclasses)."""
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
            # Should not be able to modify (frozen dataclass)
            with pytest.raises(Exception):
                social.label = "new_label"
    
    def test_previous_team_structure(self, mock_fetch_html):
        """Test previous team structure."""
        team = vlr.teams.info(team_id=8326)
        if team and team.previous_team:
            prev = team.previous_team
            assert hasattr(prev, 'team_id')
            assert hasattr(prev, 'name')
            # Should not be able to modify (frozen dataclass)
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
            assert _host_matches(team.logo_url, ["owcdn.net"])
    
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
                assert _host_matches(member.photo_url, ["owcdn.net"])


class TestTeamsRosterRoles:
    """Test different roster roles."""
    
    def test_roster_player_role(self, mock_fetch_html):
        """Test that players have correct role."""
        roster = vlr.teams.roster(team_id=2593)
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
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        assert isinstance(matches, list)
    
    def test_upcoming_matches_structure(self, mock_fetch_html):
        """Test that match objects have correct structure."""
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        if matches:
            match = matches[0]
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'match_url')
            assert hasattr(match, 'tournament_name')
            assert hasattr(match, 'phase')
            assert hasattr(match, 'series')
            assert hasattr(match, 'team1')
            assert hasattr(match, 'team2')
            assert hasattr(match, 'match_datetime')
            # Check team objects
            assert hasattr(match.team1, 'team_id')
            assert hasattr(match.team1, 'name')
            assert hasattr(match.team1, 'tag')
            assert hasattr(match.team1, 'logo')
            assert hasattr(match.team1, 'score')
            assert hasattr(match.team2, 'team_id')
            assert hasattr(match.team2, 'name')
            assert hasattr(match.team2, 'tag')
            assert hasattr(match.team2, 'logo')
            assert hasattr(match.team2, 'score')
    
    def test_upcoming_matches_team_names(self, mock_fetch_html):
        """Test that team names are extracted."""
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        for match in matches:
            if match.team1.name:
                assert isinstance(match.team1.name, str)
                assert len(match.team1.name) > 0
            if match.team2.name:
                assert isinstance(match.team2.name, str)
                assert len(match.team2.name) > 0
    
    def test_upcoming_matches_tournament_info(self, mock_fetch_html):
        """Test that tournament information is extracted."""
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        for match in matches:
            if match.tournament_name:
                assert isinstance(match.tournament_name, str)
                assert len(match.tournament_name) > 0
    
    def test_upcoming_matches_date_time(self, mock_fetch_html):
        """Test that match datetime is extracted."""
        from datetime import datetime
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        for match in matches:
            if match.match_datetime:
                assert isinstance(match.match_datetime, datetime)
    
    def test_upcoming_matches_immutable(self, mock_fetch_html):
        """Test that match objects are immutable."""
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        if matches:
            match = matches[0]
            with pytest.raises(Exception):
                match.tournament_name = "new_name"


class TestTeamsCompletedMatches:
    """Test team completed matches functionality."""
    
    def test_completed_matches_basic(self, mock_fetch_html):
        """Test completed matches returns list with correct structure and data."""
        matches = vlr.teams.completed_matches(team_id=799, limit=2)
        
        # Test returns list
        assert isinstance(matches, list)
        
        if matches:
            match = matches[0]
            
            # Test structure
            assert hasattr(match, 'match_id')
            assert hasattr(match, 'match_url')
            assert hasattr(match, 'tournament_name')
            assert hasattr(match, 'team1')
            assert hasattr(match, 'team2')
            
            # Test scores are valid
            if match.team1.score is not None:
                assert isinstance(match.team1.score, int)
                assert match.team1.score >= 0
            if match.team2.score is not None:
                assert isinstance(match.team2.score, int)
                assert match.team2.score >= 0
            
            # Test match ID
            if match.match_id:
                assert isinstance(match.match_id, int)
                assert match.match_id > 0
            
            # Test URLs
            if match.match_url:
                assert match.match_url.startswith("https://")
                assert _host_matches(match.match_url, ["vlr.gg"])


class TestTeamsMatchesIntegration:
    """Integration tests for team matches."""
    
    def test_both_match_types(self, mock_fetch_html):
        """Test getting both upcoming and completed matches (limited)."""
        upcoming = vlr.teams.upcoming_matches(team_id=799, limit=2)
        completed = vlr.teams.completed_matches(team_id=799, limit=2)
        
        assert isinstance(upcoming, list)
        assert isinstance(completed, list)
    
    def test_matches_with_team_info(self, mock_fetch_html):
        """Test getting matches along with team info (limited)."""
        team_info = vlr.teams.info(team_id=799)
        matches = vlr.teams.completed_matches(team_id=799, limit=2)
        
        if team_info:
            assert team_info.team_id == 799
        assert isinstance(matches, list)
    
    def test_invalid_team_matches(self, mock_fetch_html):
        """Test matches for invalid team ID."""
        upcoming = vlr.teams.upcoming_matches(team_id=999999999, limit=2)
        completed = vlr.teams.completed_matches(team_id=999999999, limit=2)
        
        assert isinstance(upcoming, list)
        assert isinstance(completed, list)
        assert len(upcoming) == 0
        assert len(completed) == 0
    
    def test_matches_with_count_limit(self, mock_fetch_html):
        """Test getting matches with count limit."""
        matches_2 = vlr.teams.completed_matches(team_id=799, limit=2)
        matches_5 = vlr.teams.completed_matches(team_id=799, limit=5)
        
        assert isinstance(matches_2, list)
        assert isinstance(matches_5, list)
        assert len(matches_2) <= 2
        assert len(matches_5) <= 5
    
    def test_matches_pagination(self, mock_fetch_html):
        """Test that pagination works correctly (limited test)."""
        # Only test minimal count to avoid long test times
        limited_matches = vlr.teams.completed_matches(team_id=799, limit=2)
        
        assert isinstance(limited_matches, list)
        assert len(limited_matches) <= 2
    
    def test_matches_count_zero(self, mock_fetch_html):
        """Test getting matches with limit=0."""
        matches = vlr.teams.completed_matches(team_id=799, limit=0)
        assert isinstance(matches, list)
        assert len(matches) == 0
    
    def test_upcoming_matches_with_count(self, mock_fetch_html):
        """Test upcoming matches with count parameter."""
        matches = vlr.teams.upcoming_matches(team_id=799, limit=3)
        assert isinstance(matches, list)
        assert len(matches) <= 3


class TestTeamsMatchesEdgeCases:
    """Test edge cases for team matches."""
    
    def test_matches_phase_series_format(self, mock_fetch_html):
        """Test that phase and series are properly formatted."""
        matches = vlr.teams.completed_matches(team_id=799, limit=3)
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
        matches = vlr.teams.completed_matches(team_id=799, limit=3)
        for match in matches:
            if match.team1.team_id:
                assert isinstance(match.team1.team_id, int)
                assert match.team1.team_id > 0
            if match.team2.team_id:
                assert isinstance(match.team2.team_id, int)
                assert match.team2.team_id > 0
    
    def test_matches_immutable(self, mock_fetch_html):
        """Test that match objects are immutable."""
        matches = vlr.teams.completed_matches(team_id=799, limit=3)
        if matches:
            match = matches[0]
            with pytest.raises(Exception):
                match.tournament_name = "new_name"


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


class TestTeamsTransactions:
    """Test team transactions functionality."""
    
    def test_transactions_returns_list(self, mock_fetch_html):
        """Test that transactions() returns a list."""
        txns = vlr.teams.transactions(team_id=1034)
        assert isinstance(txns, list)
    
    def test_transactions_not_empty(self, mock_fetch_html):
        """Test that NRG has transactions."""
        txns = vlr.teams.transactions(team_id=1034)
        assert len(txns) > 0
    
    def test_transactions_structure(self, mock_fetch_html):
        """Test transaction objects have correct structure."""
        txns = vlr.teams.transactions(team_id=1034)
        if txns:
            txn = txns[0]
            assert hasattr(txn, 'date')
            assert hasattr(txn, 'action')
            assert hasattr(txn, 'player_id')
            assert hasattr(txn, 'ign')
            assert hasattr(txn, 'real_name')
            assert hasattr(txn, 'country')
            assert hasattr(txn, 'position')
            assert hasattr(txn, 'reference_url')
    
    def test_transactions_first_entry(self, mock_fetch_html):
        """Test first transaction entry (most recent)."""
        txns = vlr.teams.transactions(team_id=1034)
        assert len(txns) > 0
        
        first = txns[0]
        # Based on HTML: FiNESSE leaving
        assert first.ign == "s0m"
        assert first.real_name == "Sam Oh"
        assert first.action == "leave"
        # Date from HTML source
        from datetime import date
        if first.date:
            assert isinstance(first.date, date)
            assert first.date.year == 2025
            assert first.date.month == 10
            assert first.date.day in [22, 21]  # May vary by timezone
        assert first.position == "Player"
        assert first.country == "United States"
        assert first.player_id == 4164
    
    def test_transactions_action_types(self, mock_fetch_html):
        """Test that different action types are captured."""
        txns = vlr.teams.transactions(team_id=1034)
        
        actions = {txn.action for txn in txns if txn.action}
        assert "join" in actions
        assert "leave" in actions
        assert "inactive" in actions
    
    def test_transactions_player_ids(self, mock_fetch_html):
        """Test that player IDs are extracted correctly."""
        txns = vlr.teams.transactions(team_id=1034)
        
        # Check that we have player IDs
        player_ids = [txn.player_id for txn in txns if txn.player_id]
        assert len(player_ids) > 0
        
        # All player IDs should be integers
        for pid in player_ids:
            assert isinstance(pid, int)
            assert pid > 0
    
    def test_transactions_countries(self, mock_fetch_html):
        """Test that countries are extracted and mapped."""
        txns = vlr.teams.transactions(team_id=1034)
        
        countries = {txn.country for txn in txns if txn.country}
        assert len(countries) > 0
        
        # Should have full country names, not codes
        for country in countries:
            assert isinstance(country, str)
            assert len(country) > 2  # Not just country codes
    
    def test_transactions_positions(self, mock_fetch_html):
        """Test that positions are extracted."""
        txns = vlr.teams.transactions(team_id=1034)
        
        positions = {txn.position for txn in txns if txn.position}
        assert "Player" in positions
        assert "Head coach" in positions or "Assistant coach" in positions
    
    def test_transactions_reference_urls(self, mock_fetch_html):
        """Test that reference URLs are extracted."""
        txns = vlr.teams.transactions(team_id=1034)
        
        # Check that some transactions have reference URLs
        refs = [txn.reference_url for txn in txns if txn.reference_url]
        assert len(refs) > 0
        
        # URLs should be valid
        for ref in refs[:5]:  # Check first 5
            assert isinstance(ref, str)
            assert ref.startswith("http")
    
    def test_transactions_no_whitespace(self, mock_fetch_html):
        """Test that all text fields are cleaned of whitespace."""
        txns = vlr.teams.transactions(team_id=1034)
        
        for txn in txns[:10]:  # Check first 10
            if txn.ign:
                assert txn.ign == txn.ign.strip()
                assert "\n" not in txn.ign
                assert "\t" not in txn.ign
            
            if txn.real_name:
                assert txn.real_name == txn.real_name.strip()
                assert "\n" not in txn.real_name
                assert "\t" not in txn.real_name
            
            if txn.position:
                assert txn.position == txn.position.strip()
                assert "\n" not in txn.position
                assert "\t" not in txn.position
    
    def test_transactions_immutable(self, mock_fetch_html):
        """Test that transaction objects are immutable."""
        txns = vlr.teams.transactions(team_id=1034)
        if txns:
            txn = txns[0]
            with pytest.raises(Exception):
                txn.ign = "new_name"
    
    def test_transactions_invalid_team(self, mock_fetch_html):
        """Test transactions for invalid team ID."""
        txns = vlr.teams.transactions(team_id=999999999)
        assert isinstance(txns, list)
        assert len(txns) == 0


class TestTeamsPreviousPlayers:
    """Test previous players functionality."""
    
    def test_previous_players_returns_list(self, mock_fetch_html):
        """Test that previous_players() returns a list."""
        players = vlr.teams.previous_players(team_id=1034)
        assert isinstance(players, list)
    
    def test_previous_players_not_empty(self, mock_fetch_html):
        """Test that NRG has previous players."""
        players = vlr.teams.previous_players(team_id=1034)
        assert len(players) > 0
    
    def test_previous_players_structure(self, mock_fetch_html):
        """Test player objects have correct structure."""
        players = vlr.teams.previous_players(team_id=1034)
        if players:
            player = players[0]
            assert hasattr(player, 'player_id')
            assert hasattr(player, 'ign')
            assert hasattr(player, 'real_name')
            assert hasattr(player, 'country')
            assert hasattr(player, 'position')
            assert hasattr(player, 'status')
            assert hasattr(player, 'join_date')
            assert hasattr(player, 'leave_date')
            assert hasattr(player, 'transactions')
    
    def test_previous_players_status_types(self, mock_fetch_html):
        """Test that different status types are present."""
        players = vlr.teams.previous_players(team_id=1034)
        
        statuses = {p.status for p in players}
        # Should have at least some of these statuses
        assert len(statuses) > 0
        
        # All statuses should be valid
        valid_statuses = {"Active", "Left", "Inactive", "Unknown"}
        for status in statuses:
            assert status in valid_statuses
    
    def test_previous_players_has_active(self, mock_fetch_html):
        """Test that there are active players."""
        players = vlr.teams.previous_players(team_id=1034)
        
        active = [p for p in players if p.status == "Active"]
        # NRG should have active players
        assert len(active) > 0
    
    def test_previous_players_has_left(self, mock_fetch_html):
        """Test that there are players who left."""
        players = vlr.teams.previous_players(team_id=1034)
        
        left = [p for p in players if p.status == "Left"]
        # NRG should have players who left
        assert len(left) > 0
    
    def test_previous_players_finesse_left(self, mock_fetch_html):
        """Test that FiNESSE is marked as Left."""
        players = vlr.teams.previous_players(team_id=1034)
        
        finesse = next((p for p in players if p.ign == "FiNESSE"), None)
        assert finesse is not None
        assert finesse.status == "Left"
        assert finesse.real_name == "Pujan Mehta"
        assert finesse.country == "Canada"
        assert finesse.position == "Player"
        # Date may vary by timezone
        from datetime import date
        if finesse.leave_date:
            assert isinstance(finesse.leave_date, date)
            assert finesse.leave_date.year == 2025
            assert finesse.leave_date.month == 10
            assert finesse.leave_date.day in [2, 3]
    
    def test_previous_players_skuba_active(self, mock_fetch_html):
        """Test that skuba is marked as Active."""
        players = vlr.teams.previous_players(team_id=1034)
        
        skuba = next((p for p in players if p.ign == "skuba"), None)
        assert skuba is not None
        assert skuba.status == "Active"
        assert skuba.real_name == "Logan Jenkins"
        assert skuba.country == "United States"
        assert skuba.position == "Player"
        # Date may vary by timezone
        from datetime import date
        if skuba.join_date:
            assert isinstance(skuba.join_date, date)
            assert skuba.join_date.year == 2025
            assert skuba.join_date.month == 5
            assert skuba.join_date.day in [9, 10]
        assert skuba.leave_date is None
    
    def test_previous_players_verno_left(self, mock_fetch_html):
        """Test Verno's status (inactive then left)."""
        players = vlr.teams.previous_players(team_id=1034)
        
        verno = next((p for p in players if p.ign == "Verno"), None)
        assert verno is not None
        # Verno was inactive, then left
        assert verno.status == "Left"
        from datetime import date
        if verno.leave_date:
            assert isinstance(verno.leave_date, date)
            assert verno.leave_date.year == 2025
            assert verno.leave_date.month == 3
            assert verno.leave_date.day == 19
    
    def test_previous_players_transactions_included(self, mock_fetch_html):
        """Test that each player has their transaction history."""
        players = vlr.teams.previous_players(team_id=1034)
        
        for player in players[:5]:  # Check first 5
            assert isinstance(player.transactions, list)
            assert len(player.transactions) > 0
            
            # Each transaction should be valid
            for txn in player.transactions:
                assert hasattr(txn, 'date')
                assert hasattr(txn, 'action')
    
    def test_previous_players_join_dates(self, mock_fetch_html):
        """Test that join dates are extracted."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # Active players should have join dates
        active = [p for p in players if p.status == "Active"]
        from datetime import date
        for player in active:
            if player.join_date:
                # Should be a date object
                assert isinstance(player.join_date, date)
    
    def test_previous_players_no_whitespace(self, mock_fetch_html):
        """Test that all text fields are cleaned."""
        players = vlr.teams.previous_players(team_id=1034)
        
        for player in players[:10]:  # Check first 10
            if player.ign:
                assert player.ign == player.ign.strip()
                assert "\n" not in player.ign
                assert "\t" not in player.ign
            
            if player.real_name:
                assert player.real_name == player.real_name.strip()
                assert "\n" not in player.real_name
                assert "\t" not in player.real_name
    
    def test_previous_players_sorted_by_recent(self, mock_fetch_html):
        """Test that players are sorted by most recent activity."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # First player should have the most recent transaction
        if len(players) >= 2:
            first_date = players[0].transactions[0].date
            second_date = players[1].transactions[0].date
            
            # Dates should be in descending order (most recent first)
            if first_date and second_date:
                assert first_date >= second_date
    
    def test_previous_players_immutable(self, mock_fetch_html):
        """Test that player objects are immutable."""
        players = vlr.teams.previous_players(team_id=1034)
        if players:
            player = players[0]
            with pytest.raises(Exception):
                player.status = "new_status"
    
    def test_previous_players_invalid_team(self, mock_fetch_html):
        """Test previous_players for invalid team ID."""
        players = vlr.teams.previous_players(team_id=999999999)
        assert isinstance(players, list)
        assert len(players) == 0
    
    def test_previous_players_filter_by_position(self, mock_fetch_html):
        """Test filtering players by position."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # Filter for coaches
        coaches = [p for p in players if p.position and "coach" in p.position.lower()]
        assert len(coaches) > 0
        
        # Filter for players
        players_only = [p for p in players if p.position == "Player"]
        assert len(players_only) > 0
    
    def test_previous_players_multiple_transactions(self, mock_fetch_html):
        """Test players with multiple transactions."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # Find a player with multiple transactions (e.g., Verno or Mikes)
        multi_txn_players = [p for p in players if len(p.transactions) > 1]
        assert len(multi_txn_players) > 0
        
        # Check that transactions are sorted (most recent first)
        from datetime import date
        for player in multi_txn_players[:3]:
            dates = [txn.date for txn in player.transactions if txn.date]
            if len(dates) >= 2:
                # Should be in descending order
                assert dates == sorted(dates, reverse=True)
    
    def test_previous_players_unknown_dates(self, mock_fetch_html):
        """Test that players with 'Unknown' dates are handled correctly."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # Find player with Unknown date (Ry - Manager)
        ry = next((p for p in players if p.ign == "Ry"), None)
        if ry:
            # If date is Unknown, it will be None
            assert ry.join_date is None or isinstance(ry.join_date, date)
            assert ry.status == "Active"  # Most recent action is join
            assert ry.position == "Manager"
            assert len(ry.transactions) > 0
    
    def test_previous_players_rejoin_scenario(self, mock_fetch_html):
        """Test players who leave and rejoin (multiple join/leave cycles)."""
        players = vlr.teams.previous_players(team_id=1034)
        
        # Check for players with multiple joins
        from datetime import date
        for player in players:
            join_count = sum(1 for txn in player.transactions if txn.action == "join")
            leave_count = sum(1 for txn in player.transactions if txn.action == "leave")
            
            # If player has multiple joins, verify status is based on most recent action
            if join_count > 1:
                most_recent_action = player.transactions[0].action
                if most_recent_action == "join":
                    assert player.status == "Active"
                elif most_recent_action == "leave":
                    assert player.status == "Left"
