"""Match-related API endpoints and models."""

from __future__ import annotations

import datetime
from typing import Literal

from dataclasses import dataclass

from bs4 import BeautifulSoup

from .config import get_config
from .countries import map_country_code
from .fetcher import fetch_html, batch_fetch_html, fetch_html_with_retry
from .exceptions import NetworkError
from .utils import extract_text, extract_match_id, extract_country_code, parse_date, extract_id_from_url

_config = get_config()


@dataclass(frozen=True)
class Team:
    """Represents a team in a match."""

    name: str
    id: int | None = None
    country: str | None = None
    score: int | None = None


# Lightweight cache for team IDs per match header
_TEAM_ID_CACHE: dict[int, tuple[int | None, int | None]] = {}


def _fetch_team_ids_batch(match_ids: list[int], timeout: float, max_workers: int = 4) -> dict[int, tuple[int | None, int | None]]:
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
    results: dict[int, tuple[int | None, int | None]] = {}
    uncached_ids: list[int] = []
    
    for match_id in match_ids:
        if match_id in _TEAM_ID_CACHE:
            results[match_id] = _TEAM_ID_CACHE[match_id]
        else:
            uncached_ids.append(match_id)
    
    # Fetch uncached matches concurrently
    if uncached_ids:
        urls = [f"{_config.vlr_base}/{match_id}" for match_id in uncached_ids]
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
                t1_href = t1_link.get("href") if t1_link else None
                t2_href = t2_link.get("href") if t2_link else None
                t1_href = t1_href if isinstance(t1_href, str) else None
                t2_href = t2_href if isinstance(t2_href, str) else None
                t1_id = extract_id_from_url(t1_href, "team")
                t2_id = extract_id_from_url(t2_href, "team")
                
                _TEAM_ID_CACHE[match_id] = (t1_id, t2_id)
                results[match_id] = (t1_id, t2_id)
            except Exception:
                _TEAM_ID_CACHE[match_id] = (None, None)
                results[match_id] = (None, None)
    
    return results


@dataclass(frozen=True)
class Match:
    """Represents a match summary."""

    match_id: int
    team1: Team
    team2: Team
    event_phase: str
    event: str
    time: str
    status: Literal["upcoming", "live", "completed"]
    date: datetime.date | None = None


def _parse_matches(html: str, include_scores: bool) -> list[Match]:
    """Parse matches from HTML with batch fetching for team IDs."""
    soup = BeautifulSoup(html, "lxml")
    # include_scores is currently not used but preserved for API compatibility
    _ = include_scores
    
    # First pass: collect all match data
    match_data: list[tuple[int, list[str], list[str | None], str, str, datetime.date | None, str, Literal["upcoming", "live", "completed"], int | None, int | None]] = []
    
    for node in soup.select("a.match-item"):
        href = node.get("href")
        href = href if isinstance(href, str) else None
        match_id = extract_match_id(href)
        if not match_id:
            continue
            
        team_blocks = node.select(".match-item-vs-team")

        teams: list[str] = []
        for tb in team_blocks[:2]:
            name_el = tb.select_one(".match-item-vs-team-name .text-of") or tb.select_one(".match-item-vs-team-name")
            name = extract_text(name_el)
            if name:
                teams.append(name)
        if len(teams) < 2:
            continue
        teams = teams[:2]

        countries: list[str | None] = []
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
        
        match_date: datetime.date | None = None
        if not date_text:
            label = node.find_previous("div", class_=["wf-label", "mod-large"])
            classes = label.get("class") if label else None
            if label and isinstance(classes, list) and "wf-label" in classes and "mod-large" in classes:
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
            status: Literal["upcoming", "live", "completed"] = "live"
        elif team1_score is not None or team2_score is not None:
            status = "completed"
        else:
            status = "upcoming"

        match_data.append((match_id, teams, countries, series, event, match_date, time_text, status, team1_score, team2_score))
    
    # Batch fetch team IDs for all matches concurrently
    match_ids = [match_id for match_id, *_ in match_data]
    team_ids_map = _fetch_team_ids_batch(match_ids, timeout=_config.default_timeout, max_workers=4)
    
    # Second pass: build Match objects with team IDs
    matches: list[Match] = []
    
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


def completed(
    limit: int | None = None,
    page: int | None = None,
    timeout: float | None = None,
) -> list[Match]:
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
    url = f"{_config.vlr_base}/matches/results"
    
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    if limit is None:
        try:
            if page:
                url = f"{url}?page={page}"
            html = fetch_html_with_retry(url, timeout=effective_timeout)
        except NetworkError:
            return []
        all_matches = _parse_matches(html, include_scores=True)
        return [m for m in all_matches if m.status == "completed"]
    
    results: list[Match] = []
    remaining = max(0, min(500, limit))
    cur_page = page or 1
    
    while remaining > 0:
        try:
            page_url = url if cur_page == 1 else f"{url}?page={cur_page}"
            html = fetch_html_with_retry(page_url, timeout=effective_timeout)
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
