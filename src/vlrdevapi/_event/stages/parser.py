
import logging
import re
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.stages.models import EventStage, EventStages
from vlrdevapi.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


def parse_event_stages(html: HTMLParser, event_id: int) -> EventStages:
    """Parse event stages from the matches page HTML.

    Args:
        html: Parsed HTML from /event/matches/{event_id} page
        event_id: Event identifier (for validation/logging)

    Returns:
        EventStages object containing a list of EventStage objects

    Raises:
        ValueError: If stages section exists but parsing fails

    """
    filter_div = html.css_first(".zx-subnav.zx-subnav--filter")
    if not filter_div:
        return EventStages(stages=[])

    opt_rows = filter_div.css(".zx-opt-row")
    stage_row = None
    for row in opt_rows:
        label = row.css_first(".zx-label")
        if label and label.text(strip=True).lower() == "stage:":
            stage_row = row
            break

    if not stage_row:
        return EventStages(stages=[])

    stages = []
    for opt in stage_row.css("a.opt"):
        stage = _parse_stage_option(opt)
        if stage:
            stages.append(stage)

    if not stages:
        msg = f"no valid stages found for event {event_id}"
        raise DataNotFoundError(msg)

    return EventStages(stages=stages)


def parse_event_page_dates(html: HTMLParser) -> dict[str, tuple[date | None, date | None]]:
    """Parse date ranges from the main event page subnav.

    The main event page (/event/{id}) has a .wf-subnav with .wf-subnav-item
    links, each containing a .ge-text-light date range and a
    .wf-subnav-item-title stage name.

    Args:
        html: Parsed HTML from /event/{event_id} page

    Returns:
        Dict mapping stage name (lowercased) to (start_date, end_date) tuple

    """
    subnav = html.css_first(".wf-subnav")
    if not subnav:
        return {}

    result: dict[str, tuple[date | None, date | None]] = {}
    for a in subnav.css("a.wf-subnav-item"):
        title_el = a.css_first(".wf-subnav-item-title")
        if not title_el:
            continue
        stage_name = title_el.text(strip=True).lower()
        if not stage_name:
            continue

        date_el = a.css_first(".ge-text-light")
        if not date_el:
            result[stage_name] = (None, None)
            continue

        date_text = date_el.text(strip=True)
        start, end = _parse_subnav_date_range(date_text, html)
        result[stage_name] = (start, end)

    return result


def merge_dates_into_stages(stages: EventStages, dates_map: dict[str, tuple[date | None, date | None]]) -> None:
    """Merge date ranges from the event page into stage objects in-place.

    Args:
        stages: EventStages object whose .stages list will be updated
        dates_map: Mapping from lowercased stage name to (start_date, end_date)

    """
    for stage in stages.stages:
        key = stage.name.lower()
        if key in dates_map:
            stage.start_date, stage.end_date = dates_map[key]


def _parse_subnav_date_range(text: str, html: HTMLParser) -> tuple[date | None, date | None]:
    """Parse a subnav date range string like 'May 30–Jun 1' or 'May 11–20'.

    These date strings lack a year, so we infer it from the event header's
    Dates desc-item (same approach as event info parsing).

    Args:
        text: Raw date text from the .ge-text-light element
        html: The full page HTML (used to extract the year from the header)

    Returns:
        (start_date, end_date) tuple

    """
    text = text.strip()
    if not text:
        return None, None

    year = _extract_year_from_header(html)

    separator = "–" if "–" in text else ("-" if "-" in text else None)  # noqa: RUF001
    if separator is None:
        d = _parse_subnav_single_date(text, year)
        return d, d

    parts = text.split(separator, 1)
    left = parts[0].strip()
    right = parts[1].strip()

    if not left or not right:
        return None, None

    end_date = _parse_subnav_single_date(right, year)
    if end_date is not None:
        start_date = _parse_subnav_partial_date(left, end_date.year)
        return start_date, end_date

    end_date = _parse_subnav_day_only(right, left, year)
    if end_date is not None:
        start_date = _parse_subnav_partial_date(left, end_date.year)
        return start_date, end_date

    return None, None


def _extract_year_from_header(html: HTMLParser) -> int | None:
    """Extract the year from the event header Dates meta item.

    Looks for something like 'Jan 22 – Feb 15, 2026' and returns 2026.
    """
    meta = html.css_first(".event-header-main-meta")
    if not meta:
        return None
    for child in meta.iter():
        if child.tag != "div":
            continue
        label_el = child.css_first(".label")
        if not label_el:
            continue
        label = label_el.text(strip=True).lower()
        if label == "dates":
            value_el = child.css_first(".value")
            if value_el:
                value_text = value_el.text(strip=True)
                year_match = re.search(r"\b(\d{4})\b", value_text)
                if year_match:
                    return int(year_match.group(1))
    return None


def _parse_subnav_single_date(text: str, year: int | None) -> date | None:
    """Parse a full or partial date string with an optional year.

    Handles:
        - 'Jun 1' (with year supplied)
        - 'Jun 1, 2026' (year embedded)
    """
    text = text.strip()
    if not text:
        return None

    if year is not None:
        for fmt in ("%b %d", "%B %d"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.replace(year=year).date()
            except ValueError:
                continue

    for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def _parse_subnav_partial_date(text: str, year: int) -> date | None:
    """Parse a partial date that may only have month+day (no year).

    Handles:
        - 'May 30' → date with given year
        - 'May 30, 2026' → date with embedded year
    """
    text = text.strip()
    if not text:
        return None

    full = _parse_subnav_single_date(text, None)
    if full is not None:
        return full

    for fmt in ("%b %d", "%B %d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(year=year).date()
        except ValueError:
            continue

    return None


def _parse_subnav_day_only(day_text: str, left_text: str, year: int | None) -> date | None:
    """Parse a bare day number like '20' when the range is 'May 11–20'.

    The month is inferred from the left side of the range.

    Args:
        day_text: The right side of the range (e.g., '20')
        left_text: The left side of the range (e.g., 'May 11')
        year: The year to use

    Returns:
        date object or None

    """
    day_text = day_text.strip()
    left_text = left_text.strip()

    if not day_text.isdigit():
        return None

    day = int(day_text)
    if day < 1 or day > 31:
        return None

    month_match = re.match(r"^(\w+)\s+\d{1,2}", left_text)
    if not month_match:
        return None

    month_str = month_match.group(1)
    for fmt in ("%b", "%B"):
        try:
            dt = datetime.strptime(month_str, fmt)
            use_year = year if year is not None else 2000
            return date(use_year, dt.month, day)
        except ValueError:
            continue

    return None


def _find_opt_row_after_label(filter_div: Node, stage_label: Node) -> Node | None:
    """Find the opt-row overflow-container that comes after the stage label."""
    elements = filter_div.css("*")

    label_index = None
    for i, el in enumerate(elements):
        if el == stage_label:
            label_index = i
            break

    if label_index is None:
        return None

    for el in elements[label_index + 1 :]:
        class_attr = el.attributes.get("class")
        if (
            el.tag == "div"
            and class_attr
            and "opt-row" in class_attr
            and "overflow-container" in class_attr
        ):
            return el

    return None


def _parse_stage_option(opt: Node) -> EventStage | None:
    """Parse a single stage option element.

    Args:
        opt: The .opt element (either <a> or <div>)

    Returns:
        EventStage object or None if invalid

    """
    name_div = opt.css_first("div")
    name = name_div.text(strip=True) if name_div else opt.text(strip=True)

    if not name:
        return None

    stage_id = None
    if opt.tag == "a":
        href = opt.attributes.get("href")
        if href:
            stage_id = _extract_series_id_from_url(href)

    if stage_id is None:
        return None

    return EventStage(name=name, id=stage_id)


def _extract_series_id_from_url(url: str) -> str | None:
    """Extract series_id from a URL.

    Args:
        url: URL string containing ?series_id= parameter

    Returns:
        The series_id value as string, or None if not found

    """
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        series_id = query.get("series_id")
        if series_id and len(series_id) > 0:
            return series_id[0]
    except (ValueError, TypeError, AttributeError):
        logger.debug("Failed to extract series_id from url: %s", url)
        return None
