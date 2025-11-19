"""Event matches functionality."""

from __future__ import annotations

import datetime
from urllib import parse
from bs4 import BeautifulSoup

from .models import Match, MatchTeam
from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html, batch_fetch_html
from ..exceptions import NetworkError
from ..utils import (
    extract_text,
    extract_id_from_url,
    extract_country_code,
    parse_date,
    parse_int,
)

_config = get_config()


def _get_match_team_ids_batch(match_ids: list[int], timeout: float, max_workers: int = 4) -> dict[int, tuple[int | None, int | None]]:
    """Get team IDs for multiple matches concurrently.
    
    Args:
        match_ids: List of match IDs
        timeout: Request timeout
        max_workers: Number of concurrent workers
    
    Returns:
        Dictionary mapping match_id to (team1_id, team2_id)
    """
    if not match_ids:
        return {}
    
    # Build URLs for all match pages
    urls = [f"{_config.vlr_base}/{match_id}" for match_id in match_ids]
    
    # Fetch all match pages concurrently
    results = batch_fetch_html(urls, timeout=timeout, max_workers=max_workers)
    
    # Parse team IDs from each page
    team_ids_map: dict[int, tuple[int | None, int | None]] = {}
    
    for match_id, url in zip(match_ids, urls):
        content = results.get(url)
        if isinstance(content, Exception) or not content:
            team_ids_map[match_id] = (None, None)
            continue
        
        try:
            soup = BeautifulSoup(content, "lxml")
            # Prefer header team links; fallback to any two distinct team links on the page
            team_links = soup.select(".match-header-link-name a[href*='/team/']")
            if len(team_links) < 2:
                # Fallback selectors seen across site variations
                team_links = soup.select(".match-header a[href*='/team/']") or soup.select("a[href*='/team/']")

            # Deduplicate by team URL while preserving order
            seen_hrefs: set[str] = set()
            unique_links: list = []
            for a in team_links:
                href = a.get("href")
                href_str = href if isinstance(href, str) else ""
                if "/team/" in href_str and href_str not in seen_hrefs:
                    seen_hrefs.add(href_str)
                    unique_links.append(href_str)
                if len(unique_links) >= 2:
                    break

            team1_id = extract_id_from_url(unique_links[0], "team") if len(unique_links) >= 1 else None
            team2_id = extract_id_from_url(unique_links[1], "team") if len(unique_links) >= 2 else None

            team_ids_map[match_id] = (team1_id, team2_id)
        except Exception:
            team_ids_map[match_id] = (None, None)
    
    return team_ids_map


def matches(event_id: int, stage: str | None = None, limit: int | None = None, timeout: float | None = None) -> list[Match]:
    """
    Get event matches with team IDs.
    
    Args:
        event_id: Event ID
        stage: Stage filter (optional)
        limit: Maximum number of matches to return (optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of event matches with team IDs extracted from match pages
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.events.matches(event_id=123, limit=20)
        >>> for match in matches:
        ...     print(f"{match.teams[0].name} (ID: {match.teams[0].id}) vs {match.teams[1].name} (ID: {match.teams[1].id})")
    """
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")

    # If a stage is provided, find the corresponding stage link and refetch the page
    if stage:
        # Collect stage options from dropdown
        dropdown = soup.select_one("span.wf-dropdown.mod-all")
        options: list = dropdown.select("a") if dropdown else []
        stage_map: dict[str, str] = {}
        for a in options:
            text = (extract_text(a) or "").strip()
            href = a.get("href")
            if not href or not isinstance(href, str):
                continue
            # Normalize text for matching
            key = text.lower()
            stage_map[key] = parse.urljoin(f"{_config.vlr_base}/", href.lstrip("/"))
        # Try to match requested stage (case-insensitive)
        target = stage.strip().lower()
        stage_url = stage_map.get(target)
        if stage_url:
            try:
                html = fetch_html(stage_url, effective_timeout)
                soup = BeautifulSoup(html, "lxml")
            except NetworkError:
                return []
    match_data: list[tuple[int, str, list[MatchTeam], str, str, str, datetime.date | None, str | None]] = []
    
    for card in soup.select("a.match-item"):
        if limit is not None and len(match_data) >= limit:
            break
        href = card.get("href")
        href_str = href if isinstance(href, str) else None
        # Robustly parse match ID from href like "/match/<id>/..." or "<id>/..."
        parts = href_str.strip("/").split("/") if href_str else []
        if parts and parts[0] == "match" and len(parts) >= 2:
            match_id = parse_int(parts[1])
        else:
            match_id = parse_int(parts[0]) if parts else None
        if not match_id:
            continue
        
        teams: list[MatchTeam] = []
        for team_el in card.select(".match-item-vs-team")[:2]:
            name_el = team_el.select_one(".match-item-vs-team-name .text-of") or team_el.select_one(".match-item-vs-team-name")
            name = extract_text(name_el)
            if not name:
                continue
            
            score_el = team_el.select_one(".match-item-vs-team-score")
            score = parse_int(extract_text(score_el)) if score_el else None
            
            country = None
            code = extract_country_code(team_el)
            if code:
                country = map_country_code(code)
            
            teams.append(MatchTeam(
                id=None,
                name=name,
                country=country,
                score=score,
                is_winner="mod-winner" in (team_el.get("class") or []),
            ))
        
        if len(teams) != 2:
            continue
        
        # Parse status
        ml = card.select_one(".match-item-eta .ml")
        match_status = "upcoming"
        if ml:
            classes_raw = ml.get("class")
            classes: list[str] = []
            if isinstance(classes_raw, list):
                classes = classes_raw
            elif isinstance(classes_raw, str):
                classes = [classes_raw]
            classes_list = classes
            if any("mod-completed" in str(c) for c in classes_list):
                match_status = "completed"
            elif any("mod-live" in str(c) or "mod-ongoing" in str(c) for c in classes_list):
                match_status = "ongoing"
        
        # Parse stage/phase
        event_el = card.select_one(".match-item-event")
        series_el = card.select_one(".match-item-event-series")
        phase = extract_text(series_el) or None
        stage_name = extract_text(event_el) or None
        if phase and stage_name:
            stage_name = stage_name.replace(phase, "").strip()
        
        # Parse date
        match_date: datetime.date | None = None
        label = card.find_previous("div", class_="wf-label mod-large")
        if label:
            texts = [frag.strip() for frag in label.find_all(string=True, recursive=False)]
            text = " ".join(t for t in texts if t)
            match_date = parse_date(text, ["%a, %B %d, %Y", "%A, %B %d, %Y", "%B %d, %Y"])
        
        time_text = extract_text(card.select_one(".match-item-time")) or None
        match_url = parse.urljoin(f"{_config.vlr_base}/", href_str.lstrip("/")) if href_str else ""
        
        match_data.append((match_id, match_url, teams, match_status, stage_name or "", phase or "", match_date, time_text))
    
    # Apply limit early to avoid fetching unnecessary team IDs
    if limit is not None and len(match_data) > limit:
        match_data = match_data[:limit]
    
    # Fetch team IDs concurrently using batch fetching (only for limited matches)
    match_ids = [match_id for match_id, _, _, _, _, _, _, _ in match_data]
    team_ids_map = _get_match_team_ids_batch(match_ids, effective_timeout, max_workers=4)
    
    results: list[Match] = []
    
    for match_id, match_url, teams, match_status, stage_name, phase, match_date, time_text in match_data:
        # Get team IDs from batch results
        team1_id, team2_id = team_ids_map.get(match_id, (None, None))
        
        # Update team IDs
        updated_teams = [
            MatchTeam(
                id=team1_id,
                name=teams[0].name,
                country=teams[0].country,
                score=teams[0].score,
                is_winner=teams[0].is_winner,
            ),
            MatchTeam(
                id=team2_id,
                name=teams[1].name,
                country=teams[1].country,
                score=teams[1].score,
                is_winner=teams[1].is_winner,
            ),
        ]
        
        results.append(Match(
            match_id=match_id,
            event_id=event_id,
            stage=stage_name,
            phase=phase,
            status=match_status,
            date=match_date,
            time=time_text,
            teams=(updated_teams[0], updated_teams[1]),
            url=match_url,
        ))
    
    return results
