"""Upcoming matches functionality."""

from __future__ import annotations

from .models import Match
from ._parser import _parse_matches
from ..config import get_config
from ..fetcher import fetch_html_with_retry
from ..exceptions import NetworkError

_config = get_config()


def upcoming(
    limit: int | None = None,
    page: int | None = None,
    timeout: float | None = None,
) -> list[Match]:
    """
    Get upcoming matches.
    
    Args:
        limit: Maximum number of matches to return (optional)
        page: Page number (1-indexed, optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of upcoming matches. Each match includes team1 and team2 with name, country, score, and team id.
        Team IDs are populated by quickly opening the match header and may be None for TBD/unknown teams.
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.matches.upcoming(limit=10)
        >>> for match in matches:
        ...     print(f"{match.team1.name} vs {match.team2.name}")
        ...     print(f"  {match.team1.country} vs {match.team2.country}")
        >>> # Team IDs may be None if a team is TBD
        >>> ids = (match.team1.id, match.team2.id)
    """
    url = f"{_config.vlr_base}/matches"
    
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html_with_retry(url, timeout=effective_timeout)
        except NetworkError:
            return []
        all_matches = _parse_matches(html, include_scores=False)
        return [m for m in all_matches if m.status == "upcoming"]
    
    results: list[Match] = []
    remaining = max(0, min(500, limit))
    cur_page = page or 1
    
    while remaining > 0:
        try:
            page_url = url if cur_page == 1 else f"{url}?page={cur_page}"
            html = fetch_html_with_retry(page_url, timeout=effective_timeout)
        except NetworkError:
            break
        
        batch = _parse_matches(html, include_scores=False)
        # Filter to only upcoming matches
        upcoming_only = [m for m in batch if m.status == "upcoming"]
        if not upcoming_only:
            break
        
        take = upcoming_only[:remaining]
        results.extend(take)
        remaining -= len(take)
        cur_page += 1
    
    return results
