"""Team matches retrieval."""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from ..constants import VLR_BASE, DEFAULT_TIMEOUT
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import TeamMatch, MatchTeam


def _parse_match_datetime(date_str: Optional[str], time_str: Optional[str]) -> Optional[datetime]:
    """
    Parse match date and time strings into a datetime object.
    
    Args:
        date_str: Date string (e.g., "2025/10/14", "October 15", "Oct 15")
        time_str: Time string (e.g., "5:50 pm", "2:30 PM PDT", "14:30")
    
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        date_str_clean = date_str.strip()
        
        # Try multiple date formats
        date_formats = [
            "%Y/%m/%d",  # 2025/10/14 (most common on VLR)
            "%Y-%m-%d",  # 2025-10-14
            "%B %d",     # October 15
            "%b %d",     # Oct 15
            "%d/%m",     # 15/10
            "%m/%d",     # 10/15
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str_clean, fmt)
                # Add current year if not included in format
                if "%Y" not in fmt:
                    from datetime import datetime as dt
                    current_year = dt.now().year
                    parsed_date = parsed_date.replace(year=current_year)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            return None
        
        # Parse time if available
        if time_str:
            time_str_clean = time_str.strip()
            
            time_formats = [
                "%I:%M %p",  # 5:50 PM or 5:50 pm
                "%I:%M%p",   # 5:50PM (no space)
                "%H:%M",     # 14:30
            ]
            
            for fmt in time_formats:
                try:
                    time_obj = datetime.strptime(time_str_clean, fmt).time()
                    parsed_date = datetime.combine(parsed_date.date(), time_obj)
                    break
                except ValueError:
                    continue
        
        return parsed_date
    except Exception:
        return None


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
        ...     if match.match_datetime:
        ...         print(f"{match.team1.name} vs {match.team2.name} - {match.match_datetime.strftime('%B %d, %Y')}")
        ...     else:
        ...         print(f"{match.team1.name} vs {match.team2.name}")
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
        ...     print(f"{match.team1.name} {match.team1.score}:{match.team2.score} {match.team2.name}")
        ...     if match.match_datetime:
        ...         print(f"  Date: {match.match_datetime.strftime('%B %d, %Y')}")
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
        date_str = None
        time_str = None
        date_el = item.select_one(".m-item-date")
        if date_el:
            date_div = date_el.select_one("div")
            if date_div:
                date_str = extract_text(date_div)
            
            # Get time (text node after the div)
            full_date_text = extract_text(date_el)
            if date_str and full_date_text.startswith(date_str):
                time_str = full_date_text[len(date_str):].strip()
        
        # Parse datetime
        match_datetime = _parse_match_datetime(date_str, time_str)
        
        # Create team objects
        team1_obj = MatchTeam(
            team_id=team1_id,
            name=team1_name,
            tag=team1_tag,
            logo=team1_logo,
            score=score_team1,
        )
        
        team2_obj = MatchTeam(
            team_id=team2_id,
            name=team2_name,
            tag=team2_tag,
            logo=team2_logo,
            score=score_team2,
        )
        
        matches.append(TeamMatch(
            match_id=match_id,
            match_url=match_url,
            tournament_name=tournament_name,
            phase=phase,
            series=series,
            team1=team1_obj,
            team2=team2_obj,
            match_datetime=match_datetime,
        ))
    
    return matches
