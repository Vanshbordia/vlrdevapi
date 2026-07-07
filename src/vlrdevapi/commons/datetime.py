"""Date and time parsing utilities for vlr.gg content."""

from datetime import UTC, date, datetime, time, tzinfo
from zoneinfo import ZoneInfo

UTC = UTC

# Default timezone — derived from the local machine so it matches the
# timezone VLR.gg server-renders based on the viewer's IP-based detection.
VLR_TIMEZONE: ZoneInfo | tzinfo = datetime.now().astimezone().tzinfo  # type: ignore[assignment]


def date_to_utc_datetime(d: date) -> datetime:
    """Convert a naive date to a UTC-aware datetime at midnight.

    Args:
        d: The naive date to convert.

    Returns:
        datetime: A UTC-aware datetime with hour/minute/second at 00:00:00.

    """
    return datetime(d.year, d.month, d.day, tzinfo=UTC)


def parse_vlr_date(text: str) -> date | None:
    """Parse a date string in vlr.gg format.

    Tries multiple date formats (``%Y/%m/%d``, ``%Y-%m-%d``,
    ``%a, %B %d, %Y``). Returns ``None`` if no format matches.

    Args:
        text: The date string to parse.

    Returns:
        date | None: The parsed date, or ``None`` if parsing fails.

    """
    text = text.strip()
    if not text:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%a, %B %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_vlr_time(text: str) -> time | None:
    """Parse a time string in vlr.gg format.

    Tries ``%I:%M %p`` (12-hour) and ``%H:%M`` (24-hour) formats.
    Returns ``None`` if no format matches.

    Args:
        text: The time string to parse.

    Returns:
        time | None: The parsed time, or ``None`` if parsing fails.

    """
    text = text.strip()
    if not text:
        return None
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def parse_vlr_datetime(
    date_text: str,
    time_text: str,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> datetime | None:
    """Parse separate date and time strings into a UTC-aware datetime.

    Combines the parsed date and time, localizes to *source_tz* (or
    ``VLR_TIMEZONE``), and converts to UTC.

    Args:
        date_text: The date string to parse.
        time_text: The time string to parse.
        source_tz: The timezone to assume for the given time. Defaults to
            ``VLR_TIMEZONE`` (America/New_York).

    Returns:
        datetime | None: A UTC-aware datetime, or ``None`` if the date
            could not be parsed.

    """
    d = parse_vlr_date(date_text)
    t = parse_vlr_time(time_text)
    if d is None:
        return None
    tz = source_tz or VLR_TIMEZONE
    naive = datetime(d.year, d.month, d.day) if t is None else datetime.combine(d, t)
    localized = naive.replace(tzinfo=tz)
    return localized.astimezone(UTC)


def parse_vlr_date_range(text: str) -> tuple[date | None, date | None]:
    """Parse a date range string (e.g. ``"Jan 5 - Feb 10, 2025"``) into start and end dates.

    Supports en-dash, em-dash, and hyphen as separators. If the right side is
    ``"TBD"``, the end date is ``None``. If no separator is found, the same
    date is returned for both start and end.

    Args:
        text: The date range string to parse.

    Returns:
        tuple[date | None, date | None]: A ``(start, end)`` tuple. Either
            value may be ``None`` if parsing fails.

    """
    text = text.strip()
    if not text:
        return None, None

    separators = ["—", "–", "-"]  # noqa: RUF001
    sep = None
    for s in separators:
        if s in text:
            sep = s
            break

    if sep is None:
        d = _parse_list_date(text)
        return d, d

    parts = text.split(sep, 1)
    left = parts[0].strip()
    right = parts[1].strip()

    if right.upper() == "TBD":
        start = _parse_list_date(left)
        return start, None

    end = _parse_list_date(right)
    if end is None:
        start = _parse_list_date(left)
        return start, None

    start = _parse_list_partial_date(left, end)
    return start, end


def _parse_list_date(text: str) -> date | None:
    """Parse a date string from list/match pages.

    Tries formats with year (``%b %d, %Y``, etc.) first, then formats
    without year (assuming the current year).

    Args:
        text: The date string to parse.

    Returns:
        date | None: The parsed date, or ``None`` if parsing fails.

    """
    text = text.strip()
    if not text:
        return None
    if text.upper() == "TBD":
        return None

    # Try formats with year first
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    # Try formats without year, assume current year
    current_year = datetime.now().year
    for fmt in ("%b %d", "%B %d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(year=current_year).date()
        except ValueError:
            continue

    return None


def _parse_list_partial_date(text: str, reference: date) -> date | None:
    """Parse a potentially partial date string using a reference date for the year.

    Tries full parsing first; if that fails, attempts month-day formats
    using the reference year.

    Args:
        text: The date string to parse.
        reference: A reference date whose year is used when the string
            contains no year.

    Returns:
        date | None: The parsed date, or ``None`` if parsing fails.

    """
    text = text.strip()
    if not text:
        return None
    full = _parse_list_date(text)
    if full is not None:
        return full
    for fmt in ("%b %d", "%B %d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(year=reference.year).date()
        except ValueError:
            continue
    return None
