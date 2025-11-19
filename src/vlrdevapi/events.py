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
from typing import Literal
from urllib import parse
from enum import Enum
from dateutil import parser as dateutil_parser

from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from bs4.element import Tag

from .config import get_config
from .countries import map_country_code, COUNTRY_MAP
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import (
    extract_text,
    extract_id_from_url,
    extract_country_code,
    split_date_range,
    parse_date,
    parse_int,
    normalize_whitespace,
)

_config = get_config()


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

_TIER_TO_ID: dict[str, str] = {
    "all": "all",
    "vct": "60",
    "vcl": "61",
    "t3": "62",
    "gc": "63",
    "cg": "64",
    "offseason": "67",
}


@dataclass(frozen=True)
class ListEvent:
    """Event summary from events listing."""

    id: int
    name: str
    status: Literal["upcoming", "ongoing", "completed"]
    url: str
    region: str | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    start_text: str | None = None
    end_text: str | None = None
    prize: str | None = None


@dataclass(frozen=True)
class Info:
    """Event header/info details."""

    id: int
    name: str
    subtitle: str | None = None
    date_text: str | None = None
    prize: str | None = None
    location: str | None = None
    regions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MatchTeam:
    """Team in an event match."""

    name: str
    id: int | None = None
    country: str | None = None
    score: int | None = None
    is_winner: bool | None = None


@dataclass(frozen=True)
class Match:
    """Event match entry."""

    match_id: int
    event_id: int
    status: str
    teams: tuple["MatchTeam", "MatchTeam"]
    url: str
    stage: str | None = None
    phase: str | None = None
    date: datetime.date | None = None
    time: str | None = None


@dataclass(frozen=True)
class StageMatches:
    """Match summary for a stage."""

    name: str
    match_count: int
    completed: int
    upcoming: int
    ongoing: int
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None


@dataclass(frozen=True)
class MatchSummary:
    """Event matches summary."""

    event_id: int
    total_matches: int
    completed: int
    upcoming: int
    ongoing: int
    stages: list["StageMatches"] = field(default_factory=list)


@dataclass(frozen=True)
class StandingEntry:
    """Single standing entry."""

    place: str
    prize: str | None = None
    team_id: int | None = None
    team_name: str | None = None
    team_country: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Standings:
    """Event standings."""

    event_id: int
    stage_path: str
    url: str
    entries: list["StandingEntry"] = field(default_factory=list)


@dataclass(frozen=True)
class EventStage:
    """Available stage option for an event matches page."""

    name: str
    series_id: str
    url: str


def _get_event_dates_from_matches(event_id: int, timeout: float) -> tuple[datetime.date | None, datetime.date | None]:
    """
    Fetch first and last match dates from event matches page as fallback.
    
    Args:
        event_id: Event ID
        timeout: Request timeout
    
    Returns:
        Tuple of (first_match_date, last_match_date)
    """
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None, None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Collect all match dates from the page
    match_dates: list[datetime.date] = []
    
    for card in soup.select("a.match-item"):
        # Parse date from the label above the match
        label = card.find_previous("div", class_="wf-label mod-large")
        if label:
            texts = [frag.strip() for frag in label.find_all(string=True, recursive=False)]
            text = " ".join(t for t in texts if t).strip()
            
            # Skip relative dates like "Today", "Yesterday", "Tomorrow"
            if text.lower() in ["today", "yesterday", "tomorrow"]:
                # Convert relative dates to actual dates
                today = datetime.date.today()
                if text.lower() == "today":
                    match_dates.append(today)
                elif text.lower() == "yesterday":
                    match_dates.append(today - datetime.timedelta(days=1))
                elif text.lower() == "tomorrow":
                    match_dates.append(today + datetime.timedelta(days=1))
                continue
            
            # Try parsing with common formats
            match_date = parse_date(text, [
                "%a, %B %d, %Y",  # Thu, September 7, 2023
                "%A, %B %d, %Y",  # Thursday, September 7, 2023
                "%B %d, %Y",      # September 7, 2023
                "%b %d, %Y",      # Sep 7, 2023
                "%d %B, %Y",      # 7 September, 2023
                "%d %b, %Y",      # 7 Sep, 2023
            ])
            
            if match_date:
                match_dates.append(match_date)
    
    if not match_dates:
        return None, None
    
    # Return earliest and latest dates
    return min(match_dates), max(match_dates)


def list_events(
    tier: EventTier | TierName = EventTier.ALL,
    region: str | None = None,
    status: EventStatus | StatusFilter = EventStatus.ALL,
    page: int = 1,
    limit: int | None = None,
    timeout: float | None = None,
) -> list[ListEvent]:
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
    base_params: dict[str, str] = {}
    tier_str = tier.value if isinstance(tier, EventTier) else tier
    status_str = status.value if isinstance(status, EventStatus) else status
    tier_id = _TIER_TO_ID.get(tier_str, "60")
    base_params["tier"] = tier_id
    
    if page > 1:
        base_params["page"] = str(page)
    
    url = f"{_config.vlr_base}/events"
    if base_params:
        url = f"{url}?{parse.urlencode(base_params)}"
    
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    results: list[ListEvent] = []
    
    for card in soup.select(".events-container a.event-item[href*='/event/']"):
        if limit is not None and len(results) >= limit:
            break
        href = card.get("href")
        if not href or not isinstance(href, str):
            continue
        
        name = extract_text(card.select_one(".event-item-title, .text-of")) or extract_text(card)
        if not name:
            continue
        
        ev_id = extract_id_from_url(href, "event")
        if not ev_id:
            continue
        
        # Parse meta
        date_text = None
        prize = None
        
        dates_el = card.select_one(".event-item-desc-item.mod-dates")
        if dates_el:
            # Extract full text from the value element to avoid cutting off year
            date_value_el = dates_el.select_one(".event-item-desc-item-value, .event-desc-item-value")
            if date_value_el:
                date_text = extract_text(date_value_el).strip() or None
            else:
                # Fallback to extracting from the whole element and removing label
                date_text = extract_text(dates_el).replace("Dates", "").strip() or None
        
        prize_el = card.select_one(".event-item-desc-item.mod-prize, .event-item-prize, .prize")
        if prize_el:
            prize = extract_text(prize_el).replace("Prize Pool", "").strip()
        
        # Parse status
        card_status = "upcoming"
        status_el = card.select_one(".event-item-desc-item-status")
        if status_el:
            classes_raw = status_el.get("class")
            classes: list[str] = []
            if isinstance(classes_raw, list):
                classes = classes_raw
            elif isinstance(classes_raw, str):
                classes = [classes_raw]
            classes_list = classes
            if any("mod-completed" in str(c) for c in classes_list):
                card_status = "completed"
            elif any("mod-ongoing" in str(c) for c in classes_list):
                card_status = "ongoing"
        
        if status_str != "all" and card_status != status_str:
            continue
        
        # Parse region
        region_name: str | None = None
        flag = card.select_one(".event-item-desc-item.mod-location .flag")
        if flag:
            code = extract_country_code(card.select_one(".event-item-desc-item.mod-location"))
            region_name = map_country_code(code) if code else None
        
        # Parse dates
        start_text, end_text = split_date_range(date_text) if date_text else (None, None)
        start_date: datetime.date | None = None
        end_date: datetime.date | None = None
        
        # Try to parse start date
        if start_text:
            try:
                parsed = dateutil_parser.parse(start_text, fuzzy=False)
                start_date = parsed.date()
            except (ValueError, TypeError, dateutil_parser.ParserError):
                # If fuzzy=False fails, try with common formats
                start_date = parse_date(start_text, [
                    "%b %d, %Y", "%B %d, %Y",  # Aug 28, 2025 or August 28, 2025
                    "%d %b, %Y", "%d %B, %Y",  # 28 Aug, 2025 or 28 August, 2025
                    "%m/%d/%Y", "%d/%m/%Y",    # 08/28/2025 or 28/08/2025
                    "%d/%b/%Y", "%d/%B/%Y",    # 28/Aug/2025 or 28/August/2025
                    "%b %d", "%B %d",          # Aug 28 or August 28 (no year)
                    "%d %b", "%d %B",          # 28 Aug or 28 August (no year)
                ])
        
        # Try to parse end date
        if end_text:
            try:
                parsed = dateutil_parser.parse(end_text, fuzzy=False)
                end_date = parsed.date()
            except (ValueError, TypeError, dateutil_parser.ParserError):
                # If fuzzy=False fails, try with common formats
                end_date = parse_date(end_text, [
                    "%b %d, %Y", "%B %d, %Y",  # Aug 28, 2025 or August 28, 2025
                    "%d %b, %Y", "%d %B, %Y",  # 28 Aug, 2025 or 28 August, 2025
                    "%m/%d/%Y", "%d/%m/%Y",    # 08/28/2025 or 28/08/2025
                    "%d/%b/%Y", "%d/%B/%Y",    # 28/Aug/2025 or 28/August/2025
                    "%b %d", "%B %d",          # Aug 28 or August 28 (no year)
                    "%d %b", "%d %B",          # 28 Aug or 28 August (no year)
                ])
        
        # Fallback: If dates are TBD or couldn't be parsed, fetch from matches page
        if (start_date is None or end_date is None) and (
            date_text is None 
            or date_text.lower() in ["tbd", "to be determined", "to be announced", "tba"]
            or (start_text and start_text.lower() in ["tbd", "tba"])
            or (end_text and end_text.lower() in ["tbd", "tba"])
        ):
            match_start, match_end = _get_event_dates_from_matches(ev_id, effective_timeout)
            if start_date is None and match_start:
                start_date = match_start
            if end_date is None and match_end:
                end_date = match_end
        
        results.append(ListEvent(
            id=ev_id,
            name=name,
            region=region_name or region,
            start_date=start_date,
            end_date=end_date,
            start_text=start_text,
            end_text=end_text,
            prize=prize,
            status=card_status,
            url=parse.urljoin(f"{_config.vlr_base}/", href.lstrip("/")),
        ))
    
    return results


def stages(event_id: int, timeout: float | None = None) -> list[EventStage]:
    """List available stages for an event's matches page.
    
    Returns a list of stage options with their series_id and URL. The special
    "All Stages" option will have series_id="all".
    """
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    soup = BeautifulSoup(html, "lxml")
    dropdown = soup.select_one("span.wf-dropdown.mod-all")
    if not dropdown:
        return []
    stages_list: list[EventStage] = []
    for a in dropdown.select("a"):
        name = (extract_text(a) or "").strip()
        href = a.get("href")
        if not href or not isinstance(href, str):
            continue
        full_url = parse.urljoin(f"{_config.vlr_base}/", href.lstrip("/"))
        # Parse series_id from query (?series_id=...)
        parsed = parse.urlparse(full_url)
        qs = parse.parse_qs(parsed.query)
        sid = (qs.get("series_id", ["all"]))[0] or "all"
        stages_list.append(EventStage(name=name, series_id=sid, url=full_url))
    return stages_list


def _normalize_regions(tags: list[str]) -> list[str]:
    """Normalize region tags according to business rules.

    Rules:
    - Allowed main regions: EMEA, Pacific, China, Americas
    - If multiple of these main regions are present, return ["international"]
    - If exactly one main region is present, keep it as first; then include only valid countries
      (any value present in COUNTRY_MAP values). Discard anything else.
    - If no main region is present, return only valid countries (if any). Otherwise, return [].
    """
    if not tags:
        return []

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_tags: list[str] = []
    for t in tags:
        t_norm = (t or "").strip()
        if not t_norm:
            continue
        if t_norm not in seen:
            seen.add(t_norm)
            unique_tags.append(t_norm)

    # Canonical main region names and case-insensitive detection
    REGION_CANON = {
        "emea": "EMEA",
        "pacific": "Pacific",
        "china": "China",
        "americas": "Americas",
    }
    country_name_set_lower = {v.lower(): v for v in COUNTRY_MAP.values()}

    # Resolve main regions case-insensitively to canonical casing
    main_regions_canonical: list[str] = []
    for t in unique_tags:
        key = t.lower()
        if key in REGION_CANON and REGION_CANON[key] not in main_regions_canonical:
            main_regions_canonical.append(REGION_CANON[key])

    # Resolve countries case-insensitively to canonical names
    countries_canonical: list[str] = []
    for t in unique_tags:
        v = country_name_set_lower.get(t.lower())
        if v and v not in countries_canonical:
            countries_canonical.append(v)

    # Exclude any country entries that are actually main regions (e.g., "China")
    countries_canonical = [c for c in countries_canonical if c not in REGION_CANON.values()]

    if len(main_regions_canonical) >= 2:
        # International followed by all detected main regions and valid countries, no duplicates
        combined = ["International"] + main_regions_canonical + countries_canonical
        seen_out: set[str] = set()
        out: list[str] = []
        for x in combined:
            if x not in seen_out:
                seen_out.add(x)
                out.append(x)
        return out

    if len(main_regions_canonical) == 1:
        combined = [main_regions_canonical[0]] + countries_canonical
        seen_out: set[str] = set()
        out: list[str] = []
        for x in combined:
            if x not in seen_out:
                seen_out.add(x)
                out.append(x)
        return out

    # No main regions; include only valid countries
    # No main regions; include only valid countries (deduped already)
    return countries_canonical


def info(event_id: int, timeout: float | None = None) -> Info | None:
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
    url = f"{_config.vlr_base}/event/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".event-header .event-desc-inner")
    if not header:
        return None
    
    name_el = header.select_one(".wf-title")
    subtitle_el = header.select_one(".event-desc-subtitle")
    
    regions: list[str] = []
    for a in header.select(".event-tag-container a"):
        txt = extract_text(a)
        if txt and txt not in regions:
            regions.append(txt)
    
    # Extract desc values
    def extract_desc_value(label: str) -> str | None:
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
        regions=_normalize_regions(regions),
    )


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
        options: list[Tag] = dropdown.select("a") if dropdown else []
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


def match_summary(event_id: int, timeout: float | None = None) -> MatchSummary | None:
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
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Count matches and organize by stage
    total = 0
    completed = 0
    upcoming = 0
    ongoing = 0
    
    # Track stage-level statistics
    stage_stats: dict[str, dict] = {}
    
    for card in soup.select("a.match-item"):
        total += 1
        
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
                completed += 1
                match_status = "completed"
            elif any("mod-live" in str(c) or "mod-ongoing" in str(c) for c in classes_list):
                ongoing += 1
                match_status = "ongoing"
            else:
                upcoming += 1
        else:
            upcoming += 1
        
        # Parse stage name
        event_el = card.select_one(".match-item-event")
        stage_name = extract_text(event_el) or "Unknown Stage"
        
        # Remove phase from stage name if present
        series_el = card.select_one(".match-item-event-series")
        phase = extract_text(series_el) or None
        if phase and stage_name:
            stage_name = stage_name.replace(phase, "").strip()
        
        # Parse date
        match_date: datetime.date | None = None
        label = card.find_previous("div", class_="wf-label mod-large")
        if label:
            texts = [frag.strip() for frag in label.find_all(string=True, recursive=False)]
            text = " ".join(t for t in texts if t)
            match_date = parse_date(text, ["%a, %B %d, %Y", "%A, %B %d, %Y", "%B %d, %Y"])
        
        # Initialize stage stats if not exists
        if stage_name not in stage_stats:
            stage_stats[stage_name] = {
                "count": 0,
                "completed": 0,
                "upcoming": 0,
                "ongoing": 0,
                "dates": []
            }
        
        # Update stage stats
        stage_stats[stage_name]["count"] += 1
        if match_status == "completed":
            stage_stats[stage_name]["completed"] += 1
        elif match_status == "ongoing":
            stage_stats[stage_name]["ongoing"] += 1
        else:
            stage_stats[stage_name]["upcoming"] += 1
        
        if match_date:
            stage_stats[stage_name]["dates"].append(match_date)
    
    # Build stage summaries
    stages: list[StageMatches] = []
    for stage_name, stats in stage_stats.items():
        dates = stats["dates"]
        start_date = min(dates) if dates else None
        end_date = max(dates) if dates else None
        
        stages.append(StageMatches(
            name=stage_name,
            match_count=stats["count"],
            completed=stats["completed"],
            upcoming=stats["upcoming"],
            ongoing=stats["ongoing"],
            start_date=start_date,
            end_date=end_date,
        ))
    
    return MatchSummary(
        event_id=event_id,
        total_matches=total,
        completed=completed,
        upcoming=upcoming,
        ongoing=ongoing,
        stages=stages,
    )


def standings(event_id: int, stage: str | None = None, timeout: float | None = None) -> Standings | None:
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
    url = f"{_config.vlr_base}/event/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Build base URL for the selected stage (if any)
    standings_url: str
    if stage:
        # Parse header subnav for stage links
        subnav = soup.select_one(".wf-card.mod-header .wf-subnav")
        stage_links: list[Tag] = subnav.select("a.wf-subnav-item") if subnav else []
        stage_map: dict[str, str] = {}
        for a in stage_links:
            title_el: Tag | None = a.select_one(".wf-subnav-item-title") if isinstance(a, Tag) else None
            name = (extract_text(title_el) or extract_text(a) or "").strip()
            href = a.get("href")
            if not href or not isinstance(href, str):
                continue
            key = name.lower()
            stage_map[key] = parse.urljoin(f"{_config.vlr_base}/", href.lstrip("/"))
        target = stage.strip().lower()
        selected = stage_map.get(target)
        if selected:
            base = selected.rstrip("/")
            standings_url = f"{base}/prize-distribution"
        else:
            # Fallback to default
            canonical_link = soup.select_one("link[rel='canonical']")
            canonical_href = canonical_link.get("href") if canonical_link else None
            canonical = canonical_href if isinstance(canonical_href, str) else None
            if not canonical:
                canonical = f"{_config.vlr_base}/event/{event_id}"
            base = canonical.rstrip("/")
            standings_url = f"{base}/prize-distribution"
    else:
        # Default "All"
        canonical_link = soup.select_one("link[rel='canonical']")
        canonical_href = canonical_link.get("href") if canonical_link else None
        canonical = canonical_href if isinstance(canonical_href, str) else None
        if not canonical:
            canonical = f"{_config.vlr_base}/event/{event_id}"
        base = canonical.rstrip("/")
        standings_url = f"{base}/prize-distribution"
    
    try:
        html = fetch_html(standings_url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Find the label element by scanning text instead of using a callable in 'string='
    labels = soup.find_all("div", class_="wf-label mod-large")
    label = None
    for el in labels:
        txt = el.get_text(strip=True)
        if txt and "Prize Distribution" in txt:
            label = el
            break
    if not label:
        return None
    
    card = label.find_next("div", class_="wf-card")
    if not card:
        return None
    
    table = card.select_one("table.wf-table")
    if not table:
        return None
    
    entries: list[StandingEntry] = []
    tbody = table.select_one("tbody")
    if tbody:
        for row in tbody.select("tr"):
            row_classes_raw = row.get("class")
            row_classes: list[str] = []
            if isinstance(row_classes_raw, list):
                row_classes = row_classes_raw
            elif isinstance(row_classes_raw, str):
                row_classes = [row_classes_raw]
            row_classes_list = row_classes
            if "standing-toggle" in row_classes_list:
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
                href = anchor.get("href", "")
                href_str = href if isinstance(href, str) else ""
                team_id = extract_id_from_url(href_str.strip("/"), "team")
                
                name_el = anchor.select_one(".standing-item-team-name")
                country_el = name_el.select_one(".ge-text-light") if name_el else None
                if country_el:
                    text = extract_text(country_el)
                    country = map_country_code(text) or text or None
                    _ = country_el.extract()
                
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
