
import re
from datetime import date, datetime

from vlrdevapi.commons.datetime import date_to_utc_datetime

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.info.models import (
    EventInfo,
    EventLocation,
    EventPrize,
    EventRegion,
    EventSeriesLink,
    EventStageTag,
)
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.commons.prizes import parse_prize_amount
import contextlib


def parse_event_info(html: HTMLParser, event_id: int) -> EventInfo:
    """Parse event info from the event page HTML.

    Args:
        html: Parsed HTML from the event page.
        event_id: Unique event identifier on vlr.gg.

    Returns:
        EventInfo object with parsed fields; fields are left at defaults
        if the corresponding section is missing.

    """
    event = EventInfo(id=event_id)

    header = html.css_first(".event-header")
    if not header:
        return event

    _parse_image(header, event)
    _parse_breadcrumb(header, event)
    _parse_title(header, event)
    _parse_desc_items(header, event)

    return event


def _parse_image(header: Node, event: EventInfo) -> None:
    """Parse the event thumbnail image URL from the header.

    Args:
        header: The event-header root node.
        event: EventInfo instance to mutate in-place.

    """
    img = header.css_first(".event-header-thumb img")
    if img:
        src = img.attributes.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        event.image_url = src


def _parse_breadcrumb(header: Node, event: EventInfo) -> None:
    """Parse breadcrumb links (series, stage, regions) from the header.

    Args:
        header: The event-header root node.
        event: EventInfo instance to mutate in-place.

    """
    bc = header.css_first(".event-header-main-bc")
    if not bc:
        return

    for child in bc.iter():
        if child.tag == "a":
            href = (child.attributes.get("href") or "").strip()
            name = child.text(strip=True)
            if href and name:
                event.series = EventSeriesLink(name=name, href=href)
            break

    tags_container = bc.css_first(".event-header-main-bc-tags")
    if not tags_container:
        return

    for a_el in tags_container.css("a"):
        href = (a_el.attributes.get("href") or "").strip()
        name = a_el.text(strip=True)
        if not href or not name:
            continue

        if "stage=" in href:
            event.stage = EventStageTag(name=name, href=href)
        elif "region=" in href:
            event.regions.append(EventRegion(name=name, href=href))
        else:
            event.regions.append(EventRegion(name=name, href=href))


def _parse_title(header: Node, event: EventInfo) -> None:
    """Parse the event title and subtitle from the header.

    Args:
        header: The event-header root node.
        event: EventInfo instance to mutate in-place.

    """
    name_el = header.css_first("h1.event-header-main-title")
    if name_el:
        event.name = name_el.text(strip=True)

    subtitle_el = header.css_first("h2.event-header-main-desc")
    if subtitle_el:
        event.subtitle = subtitle_el.text(strip=True)


def _parse_desc_items(header: Node, event: EventInfo) -> None:
    """Parse description items (dates, prize, location, region) from the header.

    Args:
        header: The event-header root node.
        event: EventInfo instance to mutate in-place.

    """
    meta = header.css_first(".event-header-main-meta")
    if not meta:
        return

    for child in meta.iter():
        if child.tag != "div":
            continue

        label_el = child.css_first(".label")
        value_el = child.css_first(".value")
        if not label_el or not value_el:
            continue

        label = label_el.text(strip=True).lower()
        value_text = value_el.text(strip=True)

        if label == "dates":
            start, end = _parse_date_range(value_text)
            event.start_date = start
            event.end_date = end
        elif label == "prize":
            event.prize = _parse_prize(value_text)
        elif label == "location":
            event.location = _parse_location(value_el, value_text)
        elif label == "region":
            event.region_location = _parse_location(value_el, value_text)


def _parse_date_range(text: str) -> tuple[datetime | None, datetime | None]:
    """Parse a date range string (e.g. 'Jan 22 - Feb 15, 2026').

    Args:
        text: Raw date range text from the page.

    Returns:
        (start_date, end_date) tuple; both are None if parsing fails.

    """
    text = text.strip()
    if not text:
        return None, None

    separator = None
    for sep in [" – ", " - ", "–", "-"]:  # noqa: RUF001
        if sep in text:
            separator = sep
            break
    if separator is not None:
        parts = text.split(separator, 1)
        left = parts[0].strip()
        right = parts[1].strip()

        end_date = _parse_single_date(right)
        if end_date is not None:
            start_date = _parse_partial_date(left, end_date)
            return (
                date_to_utc_datetime(start_date) if start_date else None,
                date_to_utc_datetime(end_date),
            )

        end_date = _parse_day_year_with_month(right, left)
        if end_date is not None:
            start_date = _parse_partial_date(left, end_date)
            return (
                date_to_utc_datetime(start_date) if start_date else None,
                date_to_utc_datetime(end_date),
            )

        return None, None
    d = _parse_single_date(text)
    return (date_to_utc_datetime(d), date_to_utc_datetime(d)) if d else (None, None)


def _parse_day_year_with_month(day_year_text: str, month_source: str) -> date | None:
    """Parse a 'day, year' string using the month from another text.

    Handles cases like right='15, 2026', left='Jan 22'.

    Args:
        day_year_text: Text containing day and year (e.g. '15, 2026').
        month_source: Text containing the month name (e.g. 'Jan 22').

    Returns:
        Constructed date, or None if parsing fails.

    """
    day_year_text = day_year_text.strip()
    month_source = month_source.strip()

    match = re.match(r"^(\d{1,2}),?\s*(\d{4})$", day_year_text)
    if not match:
        return None

    day = int(match.group(1))
    year = int(match.group(2))

    month_match = re.match(r"^(\w+)\s+\d{1,2}", month_source)
    if not month_match:
        return None

    month_str = month_match.group(1)
    for fmt in ("%b", "%B"):
        try:
            dt = datetime.strptime(month_str, fmt)
            return date(year, dt.month, day)
        except ValueError:
            continue

    return None


def _parse_single_date(text: str) -> date | None:
    """Parse a full date string in various formats.

    Tries formats like 'Jan 22, 2026', 'January 22, 2026', etc.

    Args:
        text: Raw date text.

    Returns:
        Parsed date, or None if no format matches.

    """
    text = text.strip()
    if not text:
        return None

    for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    match = re.match(r"^(\w+)\s+(\d{1,2}),?\s*(\d{4})$", text)
    if match:
        try:
            return datetime.strptime(
                f"{match.group(1)} {match.group(2)}, {match.group(3)}", "%b %d, %Y",
            ).date()
        except ValueError:
            pass

    return None


def _parse_partial_date(text: str, reference_end: date) -> date | None:
    """Parse a partial date (month+day only) using a reference year.

    Args:
        text: Partial date text (e.g. 'Jan 22').
        reference_end: Reference date whose year is used if not present.

    Returns:
        Completed date, or None if parsing fails.

    """
    text = text.strip()
    if not text:
        return None

    full_attempt = _parse_single_date(text)
    if full_attempt is not None:
        return full_attempt

    for fmt in ("%b %d", "%B %d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(year=reference_end.year).date()
        except ValueError:
            continue

    return None


def _parse_prize(text: str) -> EventPrize:
    """Parse prize text into an EventPrize model.

    Handles formats like '¥4,000,000 JPY  ~ $25,656 USD' and 'TBD'.

    Args:
        text: Raw prize text from the page.

    Returns:
        EventPrize with parsed amount, currency, and conversion info.

    """
    cleaned = text.strip()
    prize = EventPrize(raw_text=cleaned)

    if not cleaned:
        return prize

    if cleaned.upper() == "TBD":
        prize.is_tbd = True
        return prize

    converted_amount: int | None = None
    tilde_match = re.search(r"~\s*", cleaned)
    if tilde_match:
        converted_part = cleaned[tilde_match.end() :]
        converted_match = re.search(r"\$([\d,]+)", converted_part)
        if converted_match:
            with contextlib.suppress(ValueError):
                converted_amount = int(converted_match.group(1).replace(",", ""))

    primary_part = cleaned.split("~")[0].strip() if tilde_match else cleaned

    amount, currency_symbol = parse_prize_amount(primary_part)
    prize.amount = amount
    prize.currency_symbol = currency_symbol
    prize.converted_amount = converted_amount

    code_match = re.search(r"\b([A-Z]{3})\b", primary_part)
    if code_match:
        prize.currency_code = code_match.group(1)
    elif prize.currency_symbol == "$":
        prize.currency_code = "USD"

    return prize


def _parse_location(value_el: Node, value_text: str) -> EventLocation:
    """Parse location info from a description item value element.

    Args:
        value_el: The value HTML node containing flag and text.
        value_text: The raw text content of the value element.

    Returns:
        EventLocation with country (from flag) and venue text.

    """
    location = EventLocation()

    flag_el = value_el.css_first(".flag")
    if flag_el:
        class_attr = flag_el.attributes.get("class") or ""
        if "flag mod-" in class_attr:
            code = class_attr.split("mod-")[-1].split()[0]
            location.country = get_country_name(code)

    flag_text = flag_el.text(strip=True) if flag_el else ""
    remaining = value_text
    if flag_text and remaining.startswith(flag_text):
        remaining = remaining[len(flag_text) :].strip()

    if not flag_text:
        remaining = value_text.strip()

    if remaining:
        location.venue = remaining

    return location
