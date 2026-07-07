import re
from typing import Literal

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.info.models import EventPrize
from vlrdevapi._event.list.models import (
    EventList,
    EventListFilters,
    EventListItem,
    EventListPagination,
)
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.commons.datetime import parse_vlr_date_range
from vlrdevapi.commons.prizes import parse_prize_amount
import contextlib

_StatusLiteral = Literal["ongoing", "upcoming", "completed", "paused"]
_VALID_STATUSES: frozenset[str] = frozenset({"ongoing", "upcoming", "completed", "paused"})


def parse_event_list(html: HTMLParser, filters: dict) -> EventList:
    """Parse the events listing page HTML into an EventList model.

    Args:
        html: Parsed HTML from the events listing page.
        filters: Dict with keys 'tier', 'region', 'status', 'page'.

    Returns:
        EventList containing parsed events, filters, and pagination.

    """
    events: list[EventListItem] = []

    containers = html.css(".events-container-col")
    for container in containers:
        section_status = _detect_section_status(container)
        items = container.css("a.event-item")
        for item in items:
            event = _parse_event_item(item, section_status)
            if event is not None:
                events.append(event)

    if filters.get("status"):
        filter_status = str(filters["status"]).lower()
        events = [e for e in events if e.status == filter_status]

    pagination = _parse_pagination(html)
    event_filters = EventListFilters(
        tier=filters.get("tier", "all"),
        region=filters.get("region", "all"),
        status=filters.get("status"),
        page=filters.get("page", 1),
    )

    return EventList(
        events=events,
        filters=event_filters,
        pagination=pagination,
    )


def _detect_section_status(container: Node) -> _StatusLiteral:
    """Detect the status of a section container (ongoing/completed/upcoming).

    Args:
        container: The events-container-col node.

    Returns:
        One of 'ongoing', 'completed', or 'upcoming'.

    """
    label = container.css_first(".wf-label")
    if label is None:
        return "upcoming"
    text = label.text(strip=True).lower()
    if "completed" in text:
        return "completed"
    if "ongoing" in text:
        return "ongoing"
    return "upcoming"


def _parse_event_item(item: Node, section_status: _StatusLiteral) -> EventListItem | None:
    """Parse a single event item anchor into an EventListItem.

    Args:
        item: The a.event-item node.
        section_status: Fallback status from the parent section.

    Returns:
        EventListItem or None if the event ID cannot be extracted.

    """
    href = (item.attributes.get("href") or "").strip()
    event_id = _extract_event_id(href)
    if event_id is None:
        return None

    name = ""
    title_el = item.css_first(".event-item-title")
    if title_el:
        name = title_el.text(strip=True)

    status = _extract_status(item, section_status)

    prize = _parse_prize(item)

    start_date = None
    end_date = None
    dates_el = item.css_first(".event-item-desc-item.mod-dates")
    if dates_el:
        dates_text = _extract_value_text(dates_el)
        start_date, end_date = parse_vlr_date_range(dates_text)

    region = ""
    flag_el = item.css_first(".event-item-desc-item.mod-location .flag")
    if flag_el:
        class_attr = flag_el.attributes.get("class") or ""
        if "flag mod-" in class_attr:
            code = class_attr.split("mod-")[-1].split()[0]
            region = get_country_name(code)

    image_url = ""
    img_el = item.css_first(".event-item-thumb img")
    if img_el:
        src = img_el.attributes.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        image_url = src

    url = f"https://www.vlr.gg{href}" if href else ""

    return EventListItem(
        id=event_id,
        name=name,
        status=status,
        prize=prize,
        start_date=start_date,
        end_date=end_date,
        region=region,
        image_url=image_url,
        url=url,
    )


def _extract_event_id(href: str) -> int | None:
    """Extract the numeric event ID from a /event/{id} href.

    Args:
        href: URL path string.

    Returns:
        Event ID integer, or None if not matched.

    """
    match = re.match(r"^/event/(\d+)", href)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _extract_status(
    item: Node | None, section_status: _StatusLiteral,
) -> _StatusLiteral:
    """Extract match/event status from the item's status element.

    Checks for mod-ongoing, mod-upcoming, mod-completed, mod-paused classes.

    Args:
        item: The event item node.
        section_status: Fallback status from the parent section.

    Returns:
        One of 'ongoing', 'upcoming', 'completed', 'paused'.

    """
    if item is None:
        if section_status in _VALID_STATUSES:
            return section_status
        return "upcoming"

    status_el = item.css_first(".event-item-desc-item-status")
    if status_el:
        class_attr = status_el.attributes.get("class") or ""
        if "mod-ongoing" in class_attr:
            return "ongoing"
        if "mod-upcoming" in class_attr:
            return "upcoming"
        if "mod-completed" in class_attr:
            return "completed"
        if "mod-paused" in class_attr:
            return "paused"

    if section_status in _VALID_STATUSES:
        return section_status
    return "upcoming"


def _parse_prize(item: Node | None) -> EventPrize | None:
    """Parse the prize element from an event item.

    Args:
        item: The event item node.

    Returns:
        EventPrize or None if no prize element is present.

    """
    if item is None:
        return None
    prize_el = item.css_first(".event-item-desc-item.mod-prize")
    if prize_el is None:
        return None
    text = _extract_value_text(prize_el)
    if not text:
        return None
    return _build_prize(text)


def _build_prize(text: str) -> EventPrize:
    """Build an EventPrize from raw prize text.

    Args:
        text: Raw prize string (e.g. '$125,000 USD').

    Returns:
        EventPrize with parsed amount and currency.

    """
    prize = EventPrize(raw_text=text.strip())

    cleaned = text.strip()
    if not cleaned:
        return prize

    if cleaned.upper() == "TBD":
        prize.is_tbd = True
        return prize

    # Remove conversion part if present (everything after ~)
    primary_part = cleaned.split("~")[0].strip()

    amount, currency_symbol = parse_prize_amount(primary_part)
    prize.amount = amount
    prize.currency_symbol = currency_symbol
    prize.converted_amount = None

    code_match = re.search(r"\b([A-Z]{3})\b", primary_part)
    if code_match:
        prize.currency_code = code_match.group(1)

    return prize


def _extract_value_text(node: Node) -> str:
    """Extract text content excluding the label sub-element.

    Args:
        node: The parent node containing label and value text.

    Returns:
        Cleaned text with the label portion removed.

    """
    full_text = node.text()

    # Find the label div and remove its text from the full text
    label_div = node.css_first(".event-item-desc-item-label")
    if label_div:
        label_text = label_div.text()
        # Remove the label text from the full text
        full_text = full_text.replace(label_text, "").strip()

    return full_text


def _parse_pagination(html: HTMLParser) -> EventListPagination:
    """Parse pagination controls from the events listing page.

    Args:
        html: Parsed HTML from the events listing page.

    Returns:
        EventListPagination with current_page and total_pages.

    """
    container = html.css_first(".action-container-pages")
    if container is None:
        return EventListPagination()

    current_page = 1
    total_pages = 1

    active = container.css_first(".btn.mod-page.mod-active")
    if active:
        with contextlib.suppress(ValueError):
            current_page = int(active.text(strip=True))

    page_buttons = container.css(".btn.mod-page")
    for btn in page_buttons:
        btn_text = btn.text(strip=True)
        try:
            page_num = int(btn_text)
            total_pages = max(total_pages, page_num)
        except ValueError:
            href = btn.attributes.get("href") or ""
            page_match = re.search(r"page=(\d+)", href)
            if page_match:
                try:
                    page_num = int(page_match.group(1))
                    total_pages = max(total_pages, page_num)
                except ValueError:
                    pass

    total_pages = max(total_pages, current_page)

    return EventListPagination(
        current_page=current_page,
        total_pages=total_pages,
    )
