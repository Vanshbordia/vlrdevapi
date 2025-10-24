"""Team event placements retrieval."""

from __future__ import annotations

from bs4 import BeautifulSoup

from ..config import get_config
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import EventPlacement, PlacementDetail


_config = get_config()


def placements(team_id: int, timeout: float | None = None) -> list[EventPlacement]:
    """
    Get event placements for a team.
    
    Args:
        team_id: Team ID
        timeout: Request timeout in seconds
    
    Returns:
        List of event placements
    
    Example:
        >>> import vlrdevapi as vlr
        >>> placements = vlr.teams.placements(team_id=799)
        >>> for placement in placements:
        ...     print(f"{placement.event_name} ({placement.year})")
        ...     for detail in placement.placements:
        ...         print(f"  {detail.series} - {detail.place}: {detail.prize_money}")
    """
    url = f"{_config.vlr_base}/team/{team_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    placements_list: list[EventPlacement] = []
    
    # Find the "Event Placements" section (avoid lambda in 'string' for type checker)
    placements_label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        if "Event Placements" in extract_text(h2):
            placements_label = h2
            break
    if placements_label is None:
        return []
    
    # Get the card that follows
    placements_card = placements_label.find_next("div", class_="wf-card")
    if not placements_card:
        return []
    
    # Find all event items
    event_items = placements_card.select("a.team-event-item")
    
    for item in event_items:
        # Extract event URL and ID
        href_val = item.get("href")
        event_url_raw = href_val if isinstance(href_val, str) else None
        event_id = extract_id_from_url(event_url_raw, "event")
        event_url = absolute_url(event_url_raw) if event_url_raw else None
        
        # Extract event name
        event_name = None
        name_div = item.select_one("div.text-of[style*='font-weight: 500']")
        if name_div:
            event_name = extract_text(name_div)
        
        # Extract year from the last direct child div (not nested)
        year = None
        # Get all direct children divs of the item
        direct_divs = item.find_all("div", recursive=False)
        if direct_divs:
            # Last div contains the year
            year = extract_text(direct_divs[-1])
        
        # Extract all placement details (can be multiple per event)
        placement_details: list[PlacementDetail] = []
        
        # Find all divs with series info
        series_divs = item.select("div[style*='margin-top: 5px']")
        
        for series_div in series_divs:
            series = None
            place = None
            prize_money = None
            
            # Extract series and place
            series_span = series_div.select_one(".team-event-item-series")
            if series_span:
                series_text = extract_text(series_span)
                # Split by the dash separator
                if "–" in series_text:
                    parts = series_text.split("–")
                    if len(parts) >= 2:
                        series = parts[0].strip()
                        place = parts[1].strip()
                elif series_text:
                    # If no dash, treat entire text as place
                    place = series_text.strip()
            
            # Extract prize money
            prize_span = series_div.select_one("span[style*='font-weight: 700']")
            if prize_span:
                prize_money = extract_text(prize_span)
            
            # Only add if we have at least some data
            if series or place or prize_money:
                placement_details.append(PlacementDetail(
                    series=series,
                    place=place,
                    prize_money=prize_money,
                ))
        
        placements_list.append(EventPlacement(
            event_id=event_id,
            event_name=event_name,
            event_url=event_url,
            placements=placement_details,
            year=year,
        ))
    
    return placements_list
