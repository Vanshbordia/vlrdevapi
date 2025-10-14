"""Team matches retrieval."""

from __future__ import annotations

from typing import List, Optional
from bs4 import BeautifulSoup

from ..constants import VLR_BASE, DEFAULT_TIMEOUT
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import TeamMatch


def _extract_match_id_from_url(url: str) -> Optional[int]:
    """
    Extract match ID from match URL.
    
    Args:
        url: Match URL (e.g., "/511536/velocity-gaming-vs-s8ul-esports...")
    
    Returns:
        Match ID or None
    """
    if not url:
        return None
    
    # Remove leading slash
    url = url.lstrip("/")
    
    # Split by slash and get first part
    parts = url.split("/")
    if parts:
        try:
            return int(parts[0])
        except (ValueError, IndexError):
            pass
    
    return None


def _get_team_ids_from_match(match_url: str, timeout: float = DEFAULT_TIMEOUT) -> tuple[Optional[int], Optional[int]]:
    """
    Get team IDs by fetching the match page.
    
    Args:
        match_url: Full match URL
        timeout: Request timeout
    
    Returns:
        Tuple of (team1_id, team2_id)
    """
    try:
        html = fetch_html(match_url, timeout)
        soup = BeautifulSoup(html, "lxml")
        
        # Find team links in the match header
        team_links = soup.select(".match-header-link")
        
        team1_id = None
        team2_id = None
        
        if len(team_links) >= 2:
            # Extract team IDs from the links
            team1_href = team_links[0].get("href", "")
            team2_href = team_links[1].get("href", "")
            
            team1_id = extract_id_from_url(team1_href, "team")
            team2_id = extract_id_from_url(team2_href, "team")
        
        return team1_id, team2_id
    except:
        return None, None


def upcoming_matches(team_id: int, count: Optional[int] = None, timeout: float = DEFAULT_TIMEOUT) -> List[TeamMatch]:
    """
    Get upcoming matches for a team.
    
    Args:
        team_id: Team ID
        count: Maximum number of matches to return (fetches across pages if needed)
        timeout: Request timeout in seconds
    
    Returns:
        List of upcoming matches
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.teams.upcoming_matches(team_id=799, count=10)
        >>> for match in matches:
        ...     print(f"{match.team1_name} vs {match.team2_name} - {match.date}")
    """
    all_matches: List[TeamMatch] = []
    page = 1
    
    while True:
        url = f"{VLR_BASE}/team/matches/{team_id}/?group=upcoming"
        if page > 1:
            url += f"&page={page}"
        
        try:
            html = fetch_html(url, timeout)
        except NetworkError:
            break
        
        matches = _parse_matches(html, timeout)
        
        if not matches:
            break
        
        all_matches.extend(matches)
        
        # If count is specified and we have enough matches, stop
        if count is not None and len(all_matches) >= count:
            return all_matches[:count]
        
        page += 1
        
        # Safety limit to prevent infinite loops
        if page > 100:
            break
    
    return all_matches


def completed_matches(team_id: int, count: Optional[int] = None, timeout: float = DEFAULT_TIMEOUT) -> List[TeamMatch]:
    """
    Get completed matches for a team.
    
    Args:
        team_id: Team ID
        count: Maximum number of matches to return (fetches across pages if needed)
        timeout: Request timeout in seconds
    
    Returns:
        List of completed matches
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.teams.completed_matches(team_id=799, count=20)
        >>> for match in matches:
        ...     print(f"{match.team1_name} {match.score_team1}:{match.score_team2} {match.team2_name}")
    """
    all_matches: List[TeamMatch] = []
    page = 1
    
    while True:
        url = f"{VLR_BASE}/team/matches/{team_id}/?group=completed"
        if page > 1:
            url += f"&page={page}"
        
        try:
            html = fetch_html(url, timeout)
        except NetworkError:
            break
        
        matches = _parse_matches(html, timeout)
        
        if not matches:
            break
        
        all_matches.extend(matches)
        
        # If count is specified and we have enough matches, stop
        if count is not None and len(all_matches) >= count:
            return all_matches[:count]
        
        page += 1
        
        # Safety limit to prevent infinite loops
        if page > 100:
            break
    
    return all_matches


def _parse_matches(html: str, timeout: float = DEFAULT_TIMEOUT) -> List[TeamMatch]:
    """
    Parse matches from HTML.
    
    Args:
        html: HTML content
        timeout: Request timeout for fetching team IDs
    
    Returns:
        List of parsed matches
    """
    soup = BeautifulSoup(html, "lxml")
    matches: List[TeamMatch] = []
    
    # Find all match items
    match_items = soup.select("a.m-item")
    
    for item in match_items:
        # Extract match URL and ID
        match_url_raw = item.get("href", "")
        match_id = _extract_match_id_from_url(match_url_raw)
        match_url = absolute_url(match_url_raw) if match_url_raw else None
        
        # Extract tournament name
        tournament_name = None
        event_el = item.select_one(".m-item-event")
        if event_el:
            # Get the tournament name from the bold div
            tournament_div = event_el.select_one("div[style*='font-weight: 700']")
            if tournament_div:
                tournament_name = extract_text(tournament_div)
        
        # Extract phase and series (e.g., "Playoffs ⋅ GF")
        phase = None
        series = None
        if event_el:
            # Get all text nodes excluding the tournament name div
            event_text = extract_text(event_el)
            
            # Remove tournament name from the beginning
            if tournament_name and event_text.startswith(tournament_name):
                series_text = event_text[len(tournament_name):].strip()
                
                # Split by the dot separator
                if "⋅" in series_text:
                    parts = series_text.split("⋅")
                    if len(parts) >= 2:
                        phase = parts[0].strip()
                        series = parts[1].strip()
                elif series_text:
                    # If no dot, treat entire text as series
                    series = series_text
        
        # Extract team 1 info (left side)
        team1_name = None
        team1_tag = None
        team1_logo = None
        
        team1_el = item.select_one(".m-item-team:not(.mod-right)")
        if team1_el:
            team1_name_el = team1_el.select_one(".m-item-team-name")
            if team1_name_el:
                team1_name = extract_text(team1_name_el)
            
            team1_tag_el = team1_el.select_one(".m-item-team-tag")
            if team1_tag_el:
                team1_tag = extract_text(team1_tag_el)
        
        # Extract team 1 logo (left logo) - skip default logos
        team1_logo_el = item.select_one(".m-item-logo:not(.mod-right) img")
        if team1_logo_el and team1_logo_el.get("src"):
            src = team1_logo_el.get("src")
            # Skip default/placeholder logos
            if src and "vlr.png" not in src and "tmp/" not in src:
                team1_logo = absolute_url(src)
        
        # Extract team 2 info (right side)
        team2_name = None
        team2_tag = None
        team2_logo = None
        
        team2_el = item.select_one(".m-item-team.mod-right")
        if team2_el:
            team2_name_el = team2_el.select_one(".m-item-team-name")
            if team2_name_el:
                team2_name = extract_text(team2_name_el)
            
            team2_tag_el = team2_el.select_one(".m-item-team-tag")
            if team2_tag_el:
                team2_tag = extract_text(team2_tag_el)
        
        # Extract team 2 logo (right logo) - skip default logos
        team2_logo_el = item.select_one(".m-item-logo.mod-right img")
        if team2_logo_el and team2_logo_el.get("src"):
            src = team2_logo_el.get("src")
            # Skip default/placeholder logos
            if src and "vlr.png" not in src and "tmp/" not in src:
                team2_logo = absolute_url(src)
        
        # Get team IDs from match page
        team1_id = None
        team2_id = None
        if match_url:
            team1_id, team2_id = _get_team_ids_from_match(match_url, timeout)
        
        # Extract scores (if available)
        score_team1 = None
        score_team2 = None
        result_el = item.select_one(".m-item-result")
        if result_el:
            score_spans = result_el.select("span")
            if len(score_spans) >= 2:
                try:
                    score_team1 = int(extract_text(score_spans[0]))
                    score_team2 = int(extract_text(score_spans[1]))
                except (ValueError, AttributeError):
                    pass
        
        # Extract date and time
        date = None
        time = None
        date_el = item.select_one(".m-item-date")
        if date_el:
            date_div = date_el.select_one("div")
            if date_div:
                date = extract_text(date_div)
            
            # Get time (text node after the div)
            full_date_text = extract_text(date_el)
            if date and full_date_text.startswith(date):
                time = full_date_text[len(date):].strip()
        
        matches.append(TeamMatch(
            match_id=match_id,
            match_url=match_url,
            tournament_name=tournament_name,
            phase=phase,
            series=series,
            team1_id=team1_id,
            team1_name=team1_name,
            team1_tag=team1_tag,
            team1_logo=team1_logo,
            team2_id=team2_id,
            team2_name=team2_name,
            team2_tag=team2_tag,
            team2_logo=team2_logo,
            score_team1=score_team1,
            score_team2=score_team2,
            date=date,
            time=time,
        ))
    
    return matches
