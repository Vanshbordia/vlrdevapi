"""Event info functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .models import Info
from ..config import get_config
from ..countries import COUNTRY_MAP
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, normalize_whitespace

_config = get_config()


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
