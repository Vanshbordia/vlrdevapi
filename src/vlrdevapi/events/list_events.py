"""Event listing functionality."""

from __future__ import annotations

import datetime
from urllib import parse
from dateutil import parser as dateutil_parser
from bs4 import BeautifulSoup

from .models import EventTier, EventStatus, TierName, StatusFilter, ListEvent, _TIER_TO_ID
from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import (
    extract_text,
    extract_id_from_url,
    extract_country_code,
    split_date_range,
    parse_date,
)

_config = get_config()


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
