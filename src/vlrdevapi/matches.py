"""Match-related API endpoints and models."""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple, Literal

from pydantic import BaseModel, Field, ConfigDict

from bs4 import BeautifulSoup

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .countries import map_country_code
from .fetcher import fetch_html
from .exceptions import NetworkError
from .utils import extract_text, extract_match_id, extract_country_code, parse_date


class Match(BaseModel):
    """Represents a match summary."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: int = Field(description="Unique match identifier")
    teams: Tuple[str, str] = Field(description="Team names (team1, team2)")
    team_countries: Tuple[Optional[str], Optional[str]] = Field(description="Team countries")
    event_phase: str = Field(description="Event phase/stage")
    event: str = Field(description="Event name")
    date: Optional[datetime.date] = Field(None, description="Match date")
    time: str = Field(description="Match time or status")
    status: Literal["upcoming", "live", "completed"] = Field(description="Match status")
    score: Optional[str] = Field(None, description="Match score (e.g., '2-1')")


def _parse_matches(html: str, include_scores: bool) -> List[Match]:
    """Parse matches from HTML."""
    soup = BeautifulSoup(html, "lxml")
    matches: List[Match] = []

    for node in soup.select("a.match-item"):
        match_id = extract_match_id(node.get("href"))
        team_blocks = node.select(".match-item-vs-team")

        teams: List[str] = []
        for tb in team_blocks[:2]:
            name_el = tb.select_one(".match-item-vs-team-name .text-of") or tb.select_one(".match-item-vs-team-name")
            name = extract_text(name_el)
            if name:
                teams.append(name)
        if len(teams) < 2:
            continue
        teams = teams[:2]

        countries: List[Optional[str]] = []
        for tb in team_blocks[:2]:
            code = extract_country_code(tb)
            countries.append(map_country_code(code) if code else None)

        event_node = node.select_one(".match-item-event")
        series_node = node.select_one(".match-item-event-series")
        time_node = node.select_one(".match-item-time") or node.select_one(".match-item-eta")
        status_node = node.select_one(".match-item-status")
        date_node = node.select_one(".match-item-date")

        series = extract_text(series_node)
        combined_event = extract_text(event_node)
        event = combined_event.replace(series, "").strip()
        time_text = extract_text(time_node)
        date_text = extract_text(date_node)
        
        match_date: Optional[datetime.date] = None
        if not date_text:
            label = node.find_previous("div", class_=["wf-label", "mod-large"])
            if label and isinstance(label.get("class"), list) and "wf-label" in label.get("class") and "mod-large" in label.get("class"):
                direct_text = label.find(string=True, recursive=False)
                date_text = (direct_text or "").strip()
        
        if date_text:
            match_date = parse_date(date_text, ["%a, %B %d, %Y", "%A, %B %d, %Y"])

        score = None
        scores = [s.get_text(strip=True) for s in node.select(".match-item-vs-team-score")]
        if len(scores) >= 2 and not all(s == "-" for s in scores):
            score = f"{scores[0]}-{scores[1]}"

        raw_status = extract_text(status_node).upper()
        if not raw_status:
            ml_status = node.select_one(".ml-status")
            raw_status = extract_text(ml_status).upper()
        
        if raw_status == "LIVE":
            status = "live"
        elif score is not None:
            status = "completed"
        else:
            status = "upcoming"

        matches.append(
            Match(
                match_id=match_id or -1,
                teams=(teams[0], teams[1]),
                team_countries=(
                    countries[0] if countries else None,
                    countries[1] if len(countries) > 1 else None,
                ),
                event_phase=series,
                event=event,
                date=match_date,
                time=time_text,
                status=status,
                score=score,
            )
        )

    return matches


def upcoming(
    limit: Optional[int] = None,
    page: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Match]:
    """
    Get upcoming matches.
    
    Args:
        limit: Maximum number of matches to return (optional)
        page: Page number (1-indexed, optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of upcoming matches.
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.matches.upcoming(limit=10)
        >>> for match in matches:
        ...     print(f"{match.teams[0]} vs {match.teams[1]}")
    """
    url = f"{VLR_BASE}/matches"
    
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html(url, timeout)
        except NetworkError:
            return []
        return _parse_matches(html, include_scores=False)
    
    results: List[Match] = []
    remaining = max(0, min(500, limit))
    cur_page = page or 1
    
    while remaining > 0:
        try:
            page_url = url if cur_page == 1 else f"{url}?page={cur_page}"
            html = fetch_html(page_url, timeout)
        except NetworkError:
            break
        
        batch = _parse_matches(html, include_scores=False)
        if not batch:
            break
        
        take = batch[:remaining]
        results.extend(take)
        remaining -= len(take)
        cur_page += 1
    
    return results


def completed(
    limit: Optional[int] = None,
    page: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Match]:
    """
    Get completed matches.
    
    Args:
        limit: Maximum number of matches to return (optional)
        page: Page number (1-indexed, optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of completed matches.
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.matches.completed(limit=10)
        >>> for match in matches:
        ...     print(f"{match.teams[0]} vs {match.teams[1]} - {match.score}")
    """
    url = f"{VLR_BASE}/matches/results"
    
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html(url, timeout)
        except NetworkError:
            return []
        return _parse_matches(html, include_scores=True)
    
    results: List[Match] = []
    remaining = max(0, min(500, limit))
    cur_page = page or 1
    
    while remaining > 0:
        try:
            page_url = url if cur_page == 1 else f"{url}?page={cur_page}"
            html = fetch_html(page_url, timeout)
        except NetworkError:
            break
        
        batch = _parse_matches(html, include_scores=True)
        if not batch:
            break
        
        take = batch[:remaining]
        results.extend(take)
        remaining -= len(take)
        cur_page += 1
    
    return results


def live(limit: Optional[int] = None, timeout: float = DEFAULT_TIMEOUT) -> List[Match]:
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
        ...     print(f"LIVE: {match.teams[0]} vs {match.teams[1]}")
    """
    try:
        html = fetch_html(f"{VLR_BASE}/matches", timeout)
    except NetworkError:
        return []
    
    all_matches = _parse_matches(html, include_scores=False)
    return [m for m in all_matches if m.status == "live"]
