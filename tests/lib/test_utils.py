"""Tests for utility functions."""

import pytest
import datetime
from vlrdevapi.utils import (
    extract_text,
    normalize_whitespace,
    absolute_url,
    parse_int,
    parse_float,
    parse_percent,
    extract_id_from_url,
    extract_match_id,
    split_date_range,
    parse_date,
    normalize_name,
)


class TestExtractText:
    """Test extract_text function."""
    
    def test_extract_text_with_none(self):
        """Test extracting text from None."""
        assert extract_text(None) == ""
    
    def test_extract_text_with_element(self):
        """Test extracting text from element."""
        from bs4 import BeautifulSoup
        html = "<div>Hello World</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        assert extract_text(element) == "Hello World"
    
    def test_extract_text_strips_whitespace(self):
        """Test that whitespace is stripped."""
        from bs4 import BeautifulSoup
        html = "<div>  Hello World  </div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        assert extract_text(element) == "Hello World"


class TestNormalizeWhitespace:
    """Test normalize_whitespace function."""
    
    def test_normalize_multiple_spaces(self):
        """Test normalizing multiple spaces."""
        assert normalize_whitespace("Hello    World") == "Hello World"
    
    def test_normalize_newlines(self):
        """Test normalizing newlines."""
        assert normalize_whitespace("Hello\nWorld") == "Hello World"
    
    def test_normalize_tabs(self):
        """Test normalizing tabs."""
        assert normalize_whitespace("Hello\tWorld") == "Hello World"
    
    def test_normalize_mixed_whitespace(self):
        """Test normalizing mixed whitespace."""
        assert normalize_whitespace("  Hello  \n  World  \t  ") == "Hello World"


class TestAbsoluteUrl:
    """Test absolute_url function."""
    
    def test_absolute_url_with_none(self):
        """Test with None input."""
        assert absolute_url(None) is None
    
    def test_absolute_url_with_full_url(self):
        """Test with full URL."""
        url = "https://www.vlr.gg/matches"
        assert absolute_url(url) == url
    
    def test_absolute_url_with_relative(self):
        """Test with relative URL."""
        assert absolute_url("/matches") == "https://www.vlr.gg/matches"
    
    def test_absolute_url_with_protocol_relative(self):
        """Test with protocol-relative URL."""
        url = "//www.vlr.gg/matches"
        assert absolute_url(url) == "https://www.vlr.gg/matches"


class TestParseInt:
    """Test parse_int function."""
    
    def test_parse_int_with_none(self):
        """Test with None input."""
        assert parse_int(None) is None
    
    def test_parse_int_with_valid_string(self):
        """Test with valid integer string."""
        assert parse_int("123") == 123
    
    def test_parse_int_with_whitespace(self):
        """Test with whitespace."""
        assert parse_int("  123  ") == 123
    
    def test_parse_int_with_invalid(self):
        """Test with invalid input."""
        assert parse_int("abc") is None
    
    def test_parse_int_with_empty(self):
        """Test with empty string."""
        assert parse_int("") is None


class TestParseFloat:
    """Test parse_float function."""
    
    def test_parse_float_with_none(self):
        """Test with None input."""
        assert parse_float(None) is None
    
    def test_parse_float_with_valid_string(self):
        """Test with valid float string."""
        assert parse_float("123.45") == 123.45
    
    def test_parse_float_with_integer(self):
        """Test with integer string."""
        assert parse_float("123") == 123.0
    
    def test_parse_float_with_text(self):
        """Test extracting float from text."""
        result = parse_float("Rating: 1.23")
        assert result == 1.23
    
    def test_parse_float_with_invalid(self):
        """Test with invalid input."""
        assert parse_float("abc") is None


class TestParsePercent:
    """Test parse_percent function."""
    
    def test_parse_percent_with_none(self):
        """Test with None input."""
        assert parse_percent(None) is None
    
    def test_parse_percent_with_percent_sign(self):
        """Test with percent sign."""
        result = parse_percent("75%")
        assert result == 0.75
    
    def test_parse_percent_without_sign(self):
        """Test without percent sign."""
        result = parse_percent("0.75")
        assert result == 0.75
    
    def test_parse_percent_large_number(self):
        """Test with large number (assumes percentage)."""
        result = parse_percent("75")
        assert result == 0.75  # 75 > 1, so treated as percentage


class TestExtractIdFromUrl:
    """Test extract_id_from_url function."""
    
    def test_extract_id_with_none(self):
        """Test with None input."""
        assert extract_id_from_url(None, "team") is None
    
    def test_extract_id_from_team_url(self):
        """Test extracting team ID."""
        url = "/team/123/team-name"
        assert extract_id_from_url(url, "team") == 123
    
    def test_extract_id_from_player_url(self):
        """Test extracting player ID."""
        url = "/player/457/player-name"
        assert extract_id_from_url(url, "player") == 457
    
    def test_extract_id_from_event_url(self):
        """Test extracting event ID."""
        url = "/event/2498/event-name"
        assert extract_id_from_url(url, "event") == 2498
    
    def test_extract_id_from_full_url(self):
        """Test with full URL."""
        url = "https://www.vlr.gg/team/123/team-name"
        assert extract_id_from_url(url, "team") == 123


class TestExtractMatchId:
    """Test extract_match_id function."""
    
    def test_extract_match_id_with_none(self):
        """Test with None input."""
        assert extract_match_id(None) is None
    
    def test_extract_match_id_from_href(self):
        """Test extracting match ID."""
        href = "/12345/match-slug"
        assert extract_match_id(href) == 12345
    
    def test_extract_match_id_with_leading_slash(self):
        """Test with leading slash."""
        href = "/12345/match-slug"
        assert extract_match_id(href) == 12345


class TestSplitDateRange:
    """Test split_date_range function."""
    
    def test_split_date_range_with_none(self):
        """Test with None input."""
        start, end = split_date_range(None)
        assert start is None
        assert end is None
    
    def test_split_date_range_simple(self):
        """Test simple date range."""
        start, end = split_date_range("Jan 2 - 5, 2025")
        assert start is not None
        assert end is not None
    
    def test_split_date_range_full_dates(self):
        """Test with full dates."""
        start, end = split_date_range("Feb 8, 2025 - Mar 1, 2025")
        assert start == "Feb 8, 2025"
        assert end == "Mar 1, 2025"


class TestParseDate:
    """Test parse_date function."""
    
    def test_parse_date_with_format(self):
        """Test parsing date with format."""
        result = parse_date("January 1, 2025", ["%B %d, %Y"])
        assert result == datetime.date(2025, 1, 1)
    
    def test_parse_date_multiple_formats(self):
        """Test with multiple formats."""
        formats = ["%Y-%m-%d", "%B %d, %Y", "%m/%d/%Y"]
        result = parse_date("2025-01-01", formats)
        assert result == datetime.date(2025, 1, 1)
    
    def test_parse_date_invalid(self):
        """Test with invalid date."""
        result = parse_date("invalid", ["%Y-%m-%d"])
        assert result is None


class TestNormalizeName:
    """Test normalize_name function."""
    
    def test_normalize_name_lowercase(self):
        """Test lowercasing."""
        assert normalize_name("TeamName") == "teamname"
    
    def test_normalize_name_remove_spaces(self):
        """Test removing spaces."""
        assert normalize_name("Team Name") == "teamname"
    
    def test_normalize_name_remove_special(self):
        """Test removing special characters."""
        assert normalize_name("Team-Name!") == "teamname"
    
    def test_normalize_name_alphanumeric(self):
        """Test keeping alphanumeric only."""
        assert normalize_name("Team123") == "team123"


class TestUtilsIntegration:
    """Integration tests for utility functions."""
    
    def test_url_parsing_chain(self):
        """Test chaining URL parsing functions."""
        url = "/team/123/team-name"
        absolute = absolute_url(url)
        team_id = extract_id_from_url(absolute, "team")
        
        assert "https://" in absolute
        assert team_id == 123
    
    def test_text_parsing_chain(self):
        """Test chaining text parsing functions."""
        text = "  Rating: 1.23  "
        normalized = normalize_whitespace(text)
        rating = parse_float(normalized)
        
        assert rating == 1.23
