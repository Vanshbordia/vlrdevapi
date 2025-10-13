"""Tests for status module."""

import pytest
import vlrdevapi as vlr


class TestStatus:
    """Test status checking functionality."""
    
    def test_check_status_returns_bool(self):
        """Test that check_status() returns a boolean."""
        result = vlr.status.check_status()
        assert isinstance(result, bool)
    
    def test_check_status_with_timeout(self):
        """Test check_status() with custom timeout."""
        result = vlr.status.check_status(timeout=10.0)
        assert isinstance(result, bool)
    
    def test_check_status_callable(self):
        """Test that check_status is callable."""
        assert callable(vlr.status.check_status)


class TestStatusIntegration:
    """Integration tests for status module."""
    
    def test_status_accessible_from_main_module(self):
        """Test that status is accessible from main module."""
        assert hasattr(vlr, 'status')
        assert hasattr(vlr.status, 'check_status')
    
    def test_check_status_function_accessible(self):
        """Test that check_status is accessible."""
        assert hasattr(vlr, 'check_status')
        result = vlr.check_status()
        assert isinstance(result, bool)
