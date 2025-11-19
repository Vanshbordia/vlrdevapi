"""Event standings functionality."""

from __future__ import annotations

from urllib import parse
from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import Standings, StandingEntry
from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, extract_id_from_url

_config = get_config()


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
