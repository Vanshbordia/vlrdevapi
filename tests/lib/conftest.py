"""Pytest configuration and fixtures for vlrdevapi tests."""

import pytest
from pathlib import Path
from typing import Callable


@pytest.fixture
def html_sources_dir() -> Path:
    """Return path to HTML sources directory."""
    return Path(__file__).parent.parent / "html_sources"


@pytest.fixture
def load_html(html_sources_dir: Path) -> Callable[[str], str]:
    """Fixture to load HTML files from test sources."""
    def _load(filename: str) -> str:
        file_path = html_sources_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"HTML source not found: {filename}")
        return file_path.read_text(encoding="utf-8")
    return _load


@pytest.fixture
def mock_fetch_html(monkeypatch, load_html):
    """Mock fetch_html to return local HTML files."""
    from vlrdevapi import fetcher
    
    # Store original function
    original_fetch = fetcher.fetch_html
    
    # Create mapping of URLs to HTML files
    url_to_file = {
        # Matches
        "https://www.vlr.gg/matches": "match_schedule_upcoming.html",
        "https://www.vlr.gg/matches/results": "match_result.html",
        "https://www.vlr.gg/matches/results?page=2": "match_result_paginated.html",

        # Events
        "https://www.vlr.gg/events": "events_default.html",
        "https://www.vlr.gg/event/2498": "event_main_page.html",
        "https://www.vlr.gg/event/matches/2498": "event_matches_page.html",

        # Player profile (s0m - 4164): Overview page only
        "https://www.vlr.gg/player/4164": "player_profile.html",
        "https://www.vlr.gg/player/matches/4164": "player_matches.html",

        # Player agent stats (noia - 17397): timespan pages
        "https://www.vlr.gg/player/17397?timespan=all": "player_profile_all.html",
        "https://www.vlr.gg/player/17397?timespan=30d": "player_profile_30d.html",
        "https://www.vlr.gg/player/17397?timespan=60d": "player_profile_60d.html",
        "https://www.vlr.gg/player/17397?timespan=90d": "player_profile_90d.html",

    }
    
    def mock_fetch(url: str, timeout: float = 5.0) -> str:
        """Mock fetch that returns local HTML."""
        # Try exact match first
        if url in url_to_file:
            return load_html(url_to_file[url])
        
        # Try to find a match by checking if URL starts with a known pattern
        for pattern, filename in url_to_file.items():
            if url.startswith(pattern.split("?")[0]):
                return load_html(filename)
        
        # If no match, try to use original (will fail in offline tests)
        return original_fetch(url, timeout)
    
    monkeypatch.setattr(fetcher, "fetch_html", mock_fetch)
    return mock_fetch


@pytest.fixture
def mock_fetch_html_with_retry(monkeypatch, load_html):
    """Mock fetch_html_with_retry to return local HTML files."""
    from vlrdevapi import fetcher
    
    url_to_file = {
        "https://www.vlr.gg/matches": "match_schedule_upcoming.html",
        "https://www.vlr.gg/matches/results": "match_result.html",
        "https://www.vlr.gg/events": "events_default.html",
        "https://www.vlr.gg/player/457": "player_profile.html",
        "https://www.vlr.gg/530935": "series_page.html",
    }
    
    def mock_fetch(url: str, timeout: float = 5.0, **kwargs) -> str:
        """Mock fetch with retry that returns local HTML."""
        for pattern, filename in url_to_file.items():
            if url.startswith(pattern.split("?")[0]):
                return load_html(filename)
        return load_html("match_schedule_upcoming.html")  # Default
    
    monkeypatch.setattr(fetcher, "fetch_html_with_retry", mock_fetch)
    return mock_fetch
