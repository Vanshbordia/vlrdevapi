"""Event-related API endpoints and models.

This module provides access to:
- events.list_events(): List all events with filters
- events.Info: Get event header/info
- events.Matches: Get event matches
- events.MatchSummary: Get event matches summary
- events.Standings: Get event standings
"""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple, Literal, Dict
from urllib import parse
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from bs4 import BeautifulSoup

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .countries import map_country_code
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import (
    extract_text,
    extract_id_from_url,
    extract_country_code,
    split_date_range,
    parse_date,
    normalize_name,
    parse_int,
    normalize_whitespace,
)


# Enums for autocomplete
class EventTier(str, Enum):
    """Event tier options."""
    ALL = "all"
    VCT = "vct"
    VCL = "vcl"
    T3 = "t3"
    GC = "gc"
    CG = "cg"
    OFFSEASON = "offseason"


class EventStatus(str, Enum):
    """Event status filter options."""
    ALL = "all"
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"


# Type aliases for backward compatibility
TierName = Literal["all", "vct", "vcl", "t3", "gc", "cg", "offseason"]
StatusFilter = Literal["all", "upcoming", "ongoing", "completed"]

_TIER_TO_ID: Dict[str, str] = {
    "all": "all",
    "vct": "60",
    "vcl": "61",
    "t3": "62",
    "gc": "63",
    "cg": "64",
    "offseason": "67",
}


class ListEvent(BaseModel):
    """Event summary from events listing."""
    
    model_config = ConfigDict(frozen=True)
    
    id: int = Field(description="Event ID")
    name: str = Field(description="Event name")
    region: Optional[str] = Field(None, description="Event region")
    tier: Optional[str] = Field(None, description="Event tier")
    start_date: Optional[datetime.date] = Field(None, description="Start date")
    end_date: Optional[datetime.date] = Field(None, description="End date")
    start_text: Optional[str] = Field(None, description="Start date text")
    end_text: Optional[str] = Field(None, description="End date text")
    prize: Optional[str] = Field(None, description="Prize pool")
    status: Literal["upcoming", "ongoing", "completed"] = Field(description="Event status")
    url: str = Field(description="Event URL")


class Info(BaseModel):
    """Event header/info details."""
    
    model_config = ConfigDict(frozen=True)
    
    id: int = Field(description="Event ID")
    name: str = Field(description="Event name")
    subtitle: Optional[str] = Field(None, description="Event subtitle")
    date_text: Optional[str] = Field(None, description="Date range text")
    prize: Optional[str] = Field(None, description="Prize pool")
    location: Optional[str] = Field(None, description="Event location")
    regions: List[str] = Field(default_factory=list, description="Event regions")


class MatchTeam(BaseModel):
    """Team in an event match."""
    
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = Field(None, description="Team ID")
    name: str = Field(description="Team name")
    country: Optional[str] = Field(None, description="Team country")
    score: Optional[int] = Field(None, description="Team score")
    is_winner: Optional[bool] = Field(None, description="Whether team won")


class Match(BaseModel):
    """Event match entry."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: int = Field(description="Match ID")
    event_id: int = Field(description="Event ID")
    stage: Optional[str] = Field(None, description="Stage name")
    phase: Optional[str] = Field(None, description="Phase name")
    status: str = Field(description="Match status")
    date: Optional[datetime.date] = Field(None, description="Match date")
    time: Optional[str] = Field(None, description="Match time")
    teams: Tuple[MatchTeam, MatchTeam] = Field(description="Match teams")
    url: str = Field(description="Match URL")


class StageMatches(BaseModel):
    """Match summary for a stage."""
    
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(description="Stage name")
    match_count: int = Field(description="Total matches")
    completed: int = Field(description="Completed matches")
    upcoming: int = Field(description="Upcoming matches")
    ongoing: int = Field(description="Ongoing matches")
    start_date: Optional[datetime.date] = Field(None, description="Stage start date")
    end_date: Optional[datetime.date] = Field(None, description="Stage end date")


class MatchSummary(BaseModel):
    """Event matches summary."""
    
    model_config = ConfigDict(frozen=True)
    
    event_id: int = Field(description="Event ID")
    total_matches: int = Field(description="Total matches")
    completed: int = Field(description="Completed matches")
    upcoming: int = Field(description="Upcoming matches")
    ongoing: int = Field(description="Ongoing matches")
    stages: List[StageMatches] = Field(default_factory=list, description="Stage summaries")


class StandingEntry(BaseModel):
    """Single standing entry."""
    
    model_config = ConfigDict(frozen=True)
    
    place: str = Field(description="Placement")
    prize: Optional[str] = Field(None, description="Prize amount")
    team_id: Optional[int] = Field(None, description="Team ID")
    team_name: Optional[str] = Field(None, description="Team name")
    team_country: Optional[str] = Field(None, description="Team country")
    note: Optional[str] = Field(None, description="Additional note")


class Standings(BaseModel):
    """Event standings."""
    
    model_config = ConfigDict(frozen=True)
    
    event_id: int = Field(description="Event ID")
    stage_path: str = Field(description="Stage path")
    entries: List[StandingEntry] = Field(default_factory=list, description="Standing entries")
    url: str = Field(description="Standings URL")


def list_events(
    tier: EventTier | TierName = EventTier.ALL,
    region: Optional[str] = None,
    status: EventStatus | StatusFilter = EventStatus.ALL,
    page: int = 1,
    limit: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[ListEvent]:
    """
    List events with filters.
    
    Args:
        tier: Event tier (use EventTier enum or string)
        region: Region filter (optional)
        status: Event status (use EventStatus enum or string)
        page: Page number (1-indexed)
        limit: Maximum number of events to return (optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of events
    
    Example:
        >>> import vlrdevapi as vlr
        >>> from vlrdevapi.events import EventTier, EventStatus
        >>> events = vlr.events.list_events(tier=EventTier.VCT, status=EventStatus.ONGOING, limit=10)
        >>> for event in events:
        ...     print(f"{event.name} - {event.status}")
    """
    base_params: Dict[str, str] = {}
    tier_str = tier.value if isinstance(tier, EventTier) else tier
    status_str = status.value if isinstance(status, EventStatus) else status
    tier_id = _TIER_TO_ID.get(tier_str, "60")
    if tier_id != "all":
        base_params["tier"] = tier_id
    
    if page > 1:
        base_params["page"] = str(page)
    
    url = f"{VLR_BASE}/events"
    if base_params:
        url = f"{url}?{parse.urlencode(base_params)}"
    
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    results: List[ListEvent] = []
    
    for card in soup.select(".events-container a.event-item[href*='/event/']"):
        if limit is not None and len(results) >= limit:
            break
        href = card.get("href")
        if not href:
            continue
        
        name = extract_text(card.select_one(".event-item-title, .text-of")) or extract_text(card)
        if not name:
            continue
        
        ev_id = extract_id_from_url(href, "event")
        if not ev_id:
            continue
        
        # Parse meta
        date_text = None
        tier_text = None
        prize = None
        
        dates_el = card.select_one(".event-item-desc-item.mod-dates")
        if dates_el:
            date_text = extract_text(dates_el).replace("Dates", "").strip() or None
        
        badge_tier = card.select_one(".event-item-desc .wf-tag, .event-item-header .wf-tag")
        if badge_tier:
            tier_text = extract_text(badge_tier)
        
        prize_el = card.select_one(".event-item-desc-item.mod-prize, .event-item-prize, .prize")
        if prize_el:
            prize = extract_text(prize_el).replace("Prize Pool", "").strip()
        
        # Parse status
        card_status = "upcoming"
        status_el = card.select_one(".event-item-desc-item-status")
        if status_el:
            classes = status_el.get("class", [])
            if any("mod-ongoing" in str(c) for c in classes):
                card_status = "ongoing"
            elif any("mod-completed" in str(c) for c in classes):
                card_status = "completed"
        
        if status_str != "all" and card_status != status_str:
            continue
        
        # Parse region
        region_name: Optional[str] = None
        flag = card.select_one(".event-item-desc-item.mod-location .flag")
        if flag:
            code = extract_country_code(card.select_one(".event-item-desc-item.mod-location"))
            region_name = map_country_code(code) if code else None
        
        # Parse dates
        start_text, end_text = split_date_range(date_text) if date_text else (None, None)
        
        results.append(ListEvent(
            id=ev_id,
            name=name,
            region=region_name or region,
            tier=tier_text or tier_str.upper() if tier_str else tier_text,
            start_date=None,
            end_date=None,
            start_text=start_text,
            end_text=end_text,
            prize=prize,
            status=card_status,
            url=parse.urljoin(f"{VLR_BASE}/", href.lstrip("/")),
        ))
    
    return results


def info(event_id: int, timeout: float = DEFAULT_TIMEOUT) -> Optional[Info]:
    """
    Get event header/info.
    
    Args:
        event_id: Event ID
        timeout: Request timeout in seconds
    
    Returns:
        Event info or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> event_info = vlr.events.info(event_id=123)
        >>> print(f"{event_info.name} - {event_info.prize}")
    """
    url = f"{VLR_BASE}/event/{event_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".event-header .event-desc-inner")
    if not header:
        return None
    
    name_el = header.select_one(".wf-title")
    subtitle_el = header.select_one(".event-desc-subtitle")
    
    regions: List[str] = []
    for a in header.select(".event-tag-container a"):
        txt = extract_text(a)
        if txt and txt not in regions:
            regions.append(txt)
    
    # Extract desc values
    def extract_desc_value(label: str) -> Optional[str]:
        for item in header.select(".event-desc-item"):
            label_el = item.select_one(".event-desc-item-label")
            if not label_el or extract_text(label_el) != label:
                continue
            value_el = item.select_one(".event-desc-item-value")
            if value_el:
                text = value_el.get_text(" ", strip=True)
                if text:
                    return text
        return None
    
    date_text = extract_desc_value("Dates")
    prize_text = extract_desc_value("Prize")
    if prize_text:
        prize_text = normalize_whitespace(prize_text)
    location_text = extract_desc_value("Location")
    
    return Info(
        id=event_id,
        name=extract_text(name_el),
        subtitle=extract_text(subtitle_el) or None,
        date_text=date_text,
        prize=prize_text,
        location=location_text,
        regions=regions,
    )


def _get_match_team_ids_batch(match_ids: List[int], timeout: float, max_workers: int = 4) -> Dict[int, Tuple[Optional[int], Optional[int]]]:
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
    urls = [f"{VLR_BASE}/{match_id}" for match_id in match_ids]
    
    # Fetch all match pages concurrently
    results = batch_fetch_html(urls, timeout=timeout, max_workers=max_workers)
    
    # Parse team IDs from each page
    team_ids_map: Dict[int, Tuple[Optional[int], Optional[int]]] = {}
    
    for match_id, url in zip(match_ids, urls):
        content = results.get(url)
        if isinstance(content, Exception) or not content:
            team_ids_map[match_id] = (None, None)
            continue
        
        try:
            soup = BeautifulSoup(content, "lxml")
            team_links = soup.select(".match-header-link-name a[href*='/team/']")
            
            team1_id = None
            team2_id = None
            
            if len(team_links) >= 1:
                href1 = team_links[0].get("href", "")
                team1_id = extract_id_from_url(href1, "team")
            
            if len(team_links) >= 2:
                href2 = team_links[1].get("href", "")
                team2_id = extract_id_from_url(href2, "team")
            
            team_ids_map[match_id] = (team1_id, team2_id)
        except Exception:
            team_ids_map[match_id] = (None, None)
    
    return team_ids_map


def matches(event_id: int, stage: Optional[str] = None, limit: Optional[int] = None, timeout: float = DEFAULT_TIMEOUT) -> List[Match]:
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
    url = f"{VLR_BASE}/event/matches/{event_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    match_data: List[Tuple[int, str, List[MatchTeam], str, str, Optional[datetime.date], Optional[str]]] = []
    
    for card in soup.select("a.match-item"):
        if limit is not None and len(match_data) >= limit:
            break
        href = card.get("href")
        match_id = parse_int(href.strip("/").split("/")[0]) if href else None
        if not match_id:
            continue
        
        teams = []
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
            classes = ml.get("class", [])
            if any("mod-completed" in str(c) for c in classes):
                match_status = "completed"
            elif any("mod-live" in str(c) or "mod-ongoing" in str(c) for c in classes):
                match_status = "ongoing"
        
        # Parse stage/phase
        event_el = card.select_one(".match-item-event")
        series_el = card.select_one(".match-item-event-series")
        phase = extract_text(series_el) or None
        stage_name = extract_text(event_el) or None
        if phase and stage_name:
            stage_name = stage_name.replace(phase, "").strip()
        
        # Parse date
        match_date = None
        label = card.find_previous("div", class_="wf-label mod-large")
        if label:
            texts = [frag.strip() for frag in label.find_all(string=True, recursive=False)]
            text = " ".join(t for t in texts if t)
            match_date = parse_date(text, ["%a, %B %d, %Y", "%A, %B %d, %Y", "%B %d, %Y"])
        
        time_text = extract_text(card.select_one(".match-item-time")) or None
        match_url = parse.urljoin(f"{VLR_BASE}/", href.lstrip("/"))
        
        match_data.append((match_id, match_url, teams, match_status, stage_name or "", phase or "", match_date, time_text))
    
    # Apply limit early to avoid fetching unnecessary team IDs
    if limit is not None and len(match_data) > limit:
        match_data = match_data[:limit]
    
    # Fetch team IDs concurrently using batch fetching (only for limited matches)
    match_ids = [match_id for match_id, _, _, _, _, _, _, _ in match_data]
    team_ids_map = _get_match_team_ids_batch(match_ids, timeout, max_workers=4)
    
    results: List[Match] = []
    
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


def match_summary(event_id: int, timeout: float = DEFAULT_TIMEOUT) -> Optional[MatchSummary]:
    """
    Get event match summary.
    
    Args:
        event_id: Event ID
        timeout: Request timeout in seconds
    
    Returns:
        Match summary or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> summary = vlr.events.match_summary(event_id=123)
        >>> print(f"Total: {summary.total_matches}, Completed: {summary.completed}")
    """
    url = f"{VLR_BASE}/event/matches/{event_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Count matches directly from HTML without fetching team IDs
    total = 0
    completed = 0
    upcoming = 0
    ongoing = 0
    
    for card in soup.select("a.match-item"):
        total += 1
        
        # Parse status
        ml = card.select_one(".match-item-eta .ml")
        match_status = "upcoming"
        if ml:
            classes = ml.get("class", [])
            if any("mod-completed" in str(c) for c in classes):
                match_status = "completed"
                completed += 1
            elif any("mod-live" in str(c) or "mod-ongoing" in str(c) for c in classes):
                match_status = "ongoing"
                ongoing += 1
            else:
                upcoming += 1
        else:
            upcoming += 1
    
    return MatchSummary(
        event_id=event_id,
        total_matches=total,
        completed=completed,
        upcoming=upcoming,
        ongoing=ongoing,
        stages=[],
    )


def standings(event_id: int, stage: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT) -> Optional[Standings]:
    """
    Get event standings.
    
    Args:
        event_id: Event ID
        stage: Stage filter (optional)
        timeout: Request timeout in seconds
    
    Returns:
        Standings or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> standings = vlr.events.standings(event_id=123)
        >>> for entry in standings.entries:
        ...     print(f"{entry.place}. {entry.team_name} - {entry.prize}")
    """
    url = f"{VLR_BASE}/event/{event_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Find canonical URL
    canonical_link = soup.select_one("link[rel='canonical']")
    canonical = canonical_link.get("href") if canonical_link else None
    if not canonical:
        canonical = f"{VLR_BASE}/event/{event_id}"
    
    base = canonical.rstrip("/")
    standings_url = f"{base}/prize-distribution"
    
    try:
        html = fetch_html(standings_url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    label = soup.find("div", class_="wf-label mod-large", string=lambda t: t and "Prize Distribution" in t)
    if not label:
        return None
    
    card = label.find_next("div", class_="wf-card")
    if not card:
        return None
    
    table = card.select_one("table.wf-table")
    if not table:
        return None
    
    entries: List[StandingEntry] = []
    tbody = table.select_one("tbody")
    if tbody:
        for row in tbody.select("tr"):
            if "standing-toggle" in row.get("class", []):
                continue
            
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            
            # Parse place
            place = extract_text(cells[0])
            
            # Parse prize
            prize_text = extract_text(cells[1]) if len(cells) > 1 else None
            
            # Parse team
            team_id = None
            team_name = None
            country = None
            
            anchor = cells[2].select_one("a.standing-item-team")
            if anchor:
                href = anchor.get("href", "").strip("/")
                team_id = extract_id_from_url(href, "team")
                
                name_el = anchor.select_one(".standing-item-team-name")
                country_el = name_el.select_one(".ge-text-light") if name_el else None
                if country_el:
                    text = extract_text(country_el)
                    country = map_country_code(text) or text or None
                    country_el.extract()
                
                if name_el:
                    team_name = extract_text(name_el) or None
                else:
                    team_name = extract_text(anchor) or None
            
            # Parse note
            note_td = cells[-1] if len(cells) > 3 else None
            note = extract_text(note_td) if note_td else None
            
            entries.append(StandingEntry(
                place=place,
                prize=prize_text,
                team_id=team_id,
                team_name=team_name,
                team_country=country,
                note=note,
            ))
    
    stage_path = base.split("/event/", 1)[-1]
    
    return Standings(
        event_id=event_id,
        stage_path=stage_path,
        entries=entries,
        url=standings_url,
    )
