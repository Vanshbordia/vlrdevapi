"""Match-related API endpoints and models."""

from __future__ import annotations

import datetime
from typing import List, Optional, Literal, Tuple, Dict

from pydantic import BaseModel, Field, ConfigDict

from bs4 import BeautifulSoup

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .countries import map_country_code
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import extract_text, extract_match_id, extract_country_code, parse_date, extract_id_from_url


class Team(BaseModel):
    """Represents a team in a match."""
    
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(description="Team name")
    id: Optional[int] = Field(None, description="Team ID")
    country: Optional[str] = Field(None, description="Team country")
    score: Optional[int] = Field(None, description="Team score")


# Lightweight cache for team IDs per match header
_TEAM_ID_CACHE: Dict[int, Tuple[Optional[int], Optional[int]]] = {}


def _fetch_team_ids_batch(match_ids: List[int], timeout: float, max_workers: int = 4) -> Dict[int, Tuple[Optional[int], Optional[int]]]:
    """Fetch team IDs for multiple matches concurrently.
    
    Args:
        match_ids: List of match IDs
        timeout: Request timeout
        max_workers: Number of concurrent workers
    
    Returns:
        Dictionary mapping match_id to (team1_id, team2_id)
    """
    if not match_ids:
        return {}
    
    # Check cache first and collect uncached IDs
    results: Dict[int, Tuple[Optional[int], Optional[int]]] = {}
    uncached_ids: List[int] = []
    
    for match_id in match_ids:
        if match_id in _TEAM_ID_CACHE:
            results[match_id] = _TEAM_ID_CACHE[match_id]
        else:
            uncached_ids.append(match_id)
    
    # Fetch uncached matches concurrently
    if uncached_ids:
        urls = [f"{VLR_BASE}/{match_id}" for match_id in uncached_ids]
        batch_results = batch_fetch_html(urls, timeout=timeout, max_workers=max_workers)
        
        for match_id, url in zip(uncached_ids, urls):
            content = batch_results.get(url)
            
            if isinstance(content, Exception) or not content:
                _TEAM_ID_CACHE[match_id] = (None, None)
                results[match_id] = (None, None)
                continue
            
            try:
                soup = BeautifulSoup(content, "lxml")
                header = soup.select_one(".wf-card.match-header")
                
                if not header:
                    _TEAM_ID_CACHE[match_id] = (None, None)
                    results[match_id] = (None, None)
                    continue
                
                t1_link = header.select_one(".match-header-link.mod-1")
                t2_link = header.select_one(".match-header-link.mod-2")
                t1_id = extract_id_from_url(t1_link.get("href") if t1_link else None, "team")
                t2_id = extract_id_from_url(t2_link.get("href") if t2_link else None, "team")
                
                _TEAM_ID_CACHE[match_id] = (t1_id, t2_id)
                results[match_id] = (t1_id, t2_id)
            except Exception:
                _TEAM_ID_CACHE[match_id] = (None, None)
                results[match_id] = (None, None)
    
    return results


class Match(BaseModel):
    """Represents a match summary."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: int = Field(description="Unique match identifier")
    team1: Team = Field(description="First team")
    team2: Team = Field(description="Second team")
    event_phase: str = Field(description="Event phase/stage")
    event: str = Field(description="Event name")
    date: Optional[datetime.date] = Field(None, description="Match date")
    time: str = Field(description="Match time or status")
    status: Literal["upcoming", "live", "completed"] = Field(description="Match status")


def _parse_matches(html: str, include_scores: bool) -> List[Match]:
    """Parse matches from HTML with batch fetching for team IDs."""
    soup = BeautifulSoup(html, "lxml")
    
    # First pass: collect all match data
    match_data: List[Tuple[int, List[str], List[Optional[str]], str, str, Optional[datetime.date], str, str, Optional[int], Optional[int]]] = []
    
    for node in soup.select("a.match-item"):
        match_id = extract_match_id(node.get("href"))
        if not match_id:
            continue
            
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

        scores = [s.get_text(strip=True) for s in node.select(".match-item-vs-team-score")]
        team1_score = None
        team2_score = None
        if len(scores) >= 2 and not all(s == "-" for s in scores):
            try:
                team1_score = int(scores[0]) if scores[0] != "-" else None
            except ValueError:
                pass
            try:
                team2_score = int(scores[1]) if scores[1] != "-" else None
            except ValueError:
                pass

        raw_status = extract_text(status_node).upper()
        if not raw_status:
            ml_status = node.select_one(".ml-status")
            raw_status = extract_text(ml_status).upper()
        
        if raw_status == "LIVE":
            status = "live"
        elif team1_score is not None or team2_score is not None:
            status = "completed"
        else:
            status = "upcoming"

        match_data.append((match_id, teams, countries, series, event, match_date, time_text, status, team1_score, team2_score))
    
    # Batch fetch team IDs for all matches concurrently
    match_ids = [match_id for match_id, _, _, _, _, _, _, _, _, _ in match_data]
    team_ids_map = _fetch_team_ids_batch(match_ids, timeout=DEFAULT_TIMEOUT, max_workers=4)
    
    # Second pass: build Match objects with team IDs
    matches: List[Match] = []
    
    for match_id, teams, countries, series, event, match_date, time_text, status, team1_score, team2_score in match_data:
        team1_id, team2_id = team_ids_map.get(match_id, (None, None))
        
        matches.append(
            Match(
                match_id=match_id,
                team1=Team(
                    name=teams[0],
                    id=team1_id,
                    country=countries[0] if countries else None,
                    score=team1_score,
                ),
                team2=Team(
                    name=teams[1],
                    id=team2_id,
                    country=countries[1] if len(countries) > 1 else None,
                    score=team2_score,
                ),
                event_phase=series,
                event=event,
                date=match_date,
                time=time_text,
                status=status,
            )
        )

    return matches


def upcoming(
    limit: Optional[int] = None,
    page: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[Match]:
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
    url = f"{VLR_BASE}/matches"
    
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html(url, timeout)
        except NetworkError:
            return []
        all_matches = _parse_matches(html, include_scores=False)
        return [m for m in all_matches if m.status == "upcoming"]
    
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
        # Filter to only upcoming matches
        upcoming_only = [m for m in batch if m.status == "upcoming"]
        if not upcoming_only:
            break
        
        take = upcoming_only[:remaining]
        results.extend(take)
        remaining -= len(take)
        cur_page += 1
    
    return results


def completed(
    limit: Optional[int] = None,
    page: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[Match]:
    """
    Get completed matches.
    
    Args:
        limit: Maximum number of matches to return (optional)
        page: Page number (1-indexed, optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of completed matches with scores.
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.matches.completed(limit=10)
        >>> for match in matches:
        ...     score = f"{match.team1.score}-{match.team2.score}"
        ...     print(f"{match.team1.name} vs {match.team2.name} - {score}")
    """
    url = f"{VLR_BASE}/matches/results"
    
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html(url, timeout)
        except NetworkError:
            return []
        all_matches = _parse_matches(html, include_scores=True)
        return [m for m in all_matches if m.status == "completed"]
    
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
        # Filter to only completed matches
        completed_only = [m for m in batch if m.status == "completed"]
        if not completed_only:
            break
        
        take = completed_only[:remaining]
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
        ...     print(f"LIVE: {match.team1.name} vs {match.team2.name}")
    """
    try:
        html = fetch_html(f"{VLR_BASE}/matches", timeout)
    except NetworkError:
        return []
    
    all_matches = _parse_matches(html, include_scores=False)
    return [m for m in all_matches if m.status == "live"]
