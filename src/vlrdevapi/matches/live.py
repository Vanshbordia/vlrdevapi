"""Live matches functionality."""

from __future__ import annotations

from .models import Match
from ._parser import _parse_matches
from ..config import get_config
from ..fetcher import fetch_html_with_retry
from ..exceptions import NetworkError

_config = get_config()


def live(limit: int | None = None, timeout: float | None = None) -> list[Match]:
    """
    Get live matches.
    
    Args:
        limit: Maximum number of matches to return (optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of live matches.
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.matches.live()
        >>> for match in matches:
        ...     print(f"LIVE: {match.team1.name} vs {match.team2.name}")
    """
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html_with_retry(f"{_config.vlr_base}/matches", timeout=effective_timeout)
    except NetworkError:
        return []
    
    all_matches = _parse_matches(html, include_scores=False)
    live_matches = [m for m in all_matches if m.status == "live"]
    if limit is not None:
        # Cap limit similarly to other endpoints for consistency
        max_take = max(0, min(500, limit))
        live_matches = live_matches[:max_take]
    return live_matches
