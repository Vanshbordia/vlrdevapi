"""Tests for exception handling."""

import pytest
from vlrdevapi.exceptions import (
    VlrdevapiError,
    NetworkError,
    ScrapingError,
    DataNotFoundError,
    RateLimitError,
)


class TestExceptions:
    """Test custom exceptions."""
    
    def test_base_exception(self):
        """Test base exception."""
        with pytest.raises(VlrdevapiError):
            raise VlrdevapiError("Test error")
    
    def test_network_error(self):
        """Test NetworkError."""
        with pytest.raises(NetworkError):
            raise NetworkError("Network error")
    
    def test_scraping_error(self):
        """Test ScrapingError."""
        with pytest.raises(ScrapingError):
            raise ScrapingError("Scraping error")
    
    def test_data_not_found_error(self):
        """Test DataNotFoundError."""
        with pytest.raises(DataNotFoundError):
            raise DataNotFoundError("Data not found")
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        with pytest.raises(RateLimitError):
            raise RateLimitError("Rate limited")
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from base."""
        assert issubclass(NetworkError, VlrdevapiError)
        assert issubclass(ScrapingError, VlrdevapiError)
        assert issubclass(DataNotFoundError, VlrdevapiError)
        assert issubclass(RateLimitError, VlrdevapiError)
