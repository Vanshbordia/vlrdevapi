"""Timezone detection for vlr.gg server-rendered content."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo

from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)

# VLR stores ``data-utc-ts`` timestamps in US Eastern time (not UTC).
VLR_STORED_TZ = ZoneInfo("America/New_York")

# Stable completed match used to detect the viewer timezone VLR.gg renders for.
REFERENCE_MATCH_PATH = "/670471/paper-rex-vs-leviat-n-valorant-masters-london-2026-gf"

# Common timezone abbreviations shown by VLR.gg's moment.js formatting.
_TZ_ABBREV_MAP: dict[str, str] = {
    "IST": "Asia/Kolkata",
    "PKT": "Asia/Karachi",
    "BST": "Europe/London",
    "GMT": "Etc/GMT",
    "UTC": "UTC",
    "ET": "America/New_York",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CT": "America/Chicago",
    "CDT": "America/Chicago",
    "MT": "America/Denver",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "PT": "America/Los_Angeles",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "AEST": "Australia/Sydney",
    "AEDT": "Australia/Sydney",
    "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul",
    "CST": "America/Chicago",
    "CHST": "Asia/Shanghai",
    "HKT": "Asia/Hong_Kong",
    "SGT": "Asia/Singapore",
    "CET": "Europe/Paris",
    "CEST": "Europe/Paris",
    "EET": "Europe/Helsinki",
    "EEST": "Europe/Helsinki",
    "WIB": "Asia/Jakarta",
    "WITA": "Asia/Makassar",
    "WIT": "Asia/Jayapura",
    "ICT": "Asia/Bangkok",
    "PHT": "Asia/Manila",
    "MSK": "Europe/Moscow",
    "GST": "Asia/Dubai",
}

_TIME_WITH_TZ_RE = re.compile(
    r"^(?P<time>\d{1,2}:\d{2}\s*(?:AM|PM))\s+(?P<tz>[A-Z]{2,5})$",
    re.IGNORECASE,
)


def parse_vlr_stored_datetime(ts_str: str) -> datetime | None:
    """Parse a VLR ``data-utc-ts`` attribute into a UTC-aware datetime.

    Despite the attribute name, VLR stores these values in ``VLR_STORED_TZ``
    (America/New_York), not UTC.

    Args:
        ts_str: Timestamp string from a ``data-utc-ts`` attribute.

    Returns:
        UTC-aware datetime, or ``None`` if parsing fails.

    """
    ts_str = ts_str.strip()
    if not ts_str:
        return None
    try:
        naive = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return naive.replace(tzinfo=VLR_STORED_TZ).astimezone(UTC)


def _zone_from_abbrev(abbrev: str) -> ZoneInfo | None:
    key = abbrev.upper()
    zone_name = _TZ_ABBREV_MAP.get(key)
    if zone_name is None:
        return None
    return ZoneInfo(zone_name)


def _detect_from_offset(
    stored_ts: str,
    displayed_time: str,
    displayed_date: str,
) -> ZoneInfo | None:
    """Infer viewer timezone by matching displayed local time to stored timestamp."""
    canonical = parse_vlr_stored_datetime(stored_ts)
    if canonical is None:
        return None

    match = _TIME_WITH_TZ_RE.match(displayed_time.strip())
    if not match:
        return None

    try:
        local_time = datetime.strptime(match.group("time").upper(), "%I:%M %p").time()
    except ValueError:
        return None

    date_formats = ("%A, %B %d", "%A, %B %d, %Y", "%B %d, %Y", "%b %d, %Y")
    local_date = None
    for fmt in date_formats:
        try:
            local_date = datetime.strptime(displayed_date.strip(), fmt).date()
            break
        except ValueError:
            continue
    if local_date is None:
        local_date = canonical.astimezone(VLR_STORED_TZ).date()

    candidates: list[ZoneInfo] = []
    seen: set[str] = set()
    for zone_name in _TZ_ABBREV_MAP.values():
        if zone_name in seen:
            continue
        seen.add(zone_name)
        candidates.append(ZoneInfo(zone_name))

    for zone in candidates:
        local_naive = datetime.combine(local_date, local_time)
        try:
            localized = local_naive.replace(tzinfo=zone)
        except Exception:
            continue
        if localized.astimezone(UTC) == canonical:
            return zone

    return None


def detect_vlr_timezone(html: HTMLParser) -> ZoneInfo | tzinfo:
    """Detect the viewer timezone VLR.gg used to render datetimes.

    Uses the reference match page's ``data-utc-ts`` attributes together with
    the user-visible local time (e.g. ``7:50 PM IST``).

    Args:
        html: Parsed HTML from any VLR.gg page that includes match header
            datetime elements (typically the reference match page).

    Returns:
        Detected :class:`~zoneinfo.ZoneInfo`, or a fallback timezone.

    """
    date_container = html.css_first(".match-header-date")
    if date_container is None:
        logger.debug("No match-header-date found; falling back to system timezone")
        return datetime.now().astimezone().tzinfo  # type: ignore[return-value]

    ts_el = date_container.css_first(".moment-tz-convert[data-utc-ts]")
    time_el = date_container.css_first(
        ".moment-tz-convert[data-moment-format='h:mm A z']",
    )
    date_el = date_container.css_first(
        ".moment-tz-convert[data-moment-format='dddd, MMMM D']",
    )

    if time_el is None:
        logger.debug("No timezone-formatted time element found; using system timezone")
        return datetime.now().astimezone().tzinfo  # type: ignore[return-value]

    displayed_time = time_el.text(strip=True)
    match = _TIME_WITH_TZ_RE.match(displayed_time)
    if match:
        zone = _zone_from_abbrev(match.group("tz"))
        if zone is not None:
            return zone

    if ts_el is not None and date_el is not None:
        stored_ts = ts_el.attributes.get("data-utc-ts", "") or ""
        zone = _detect_from_offset(stored_ts, displayed_time, date_el.text(strip=True))
        if zone is not None:
            return zone

    logger.debug("Could not detect VLR timezone from %r; using system timezone", displayed_time)
    return datetime.now().astimezone().tzinfo  # type: ignore[return-value]


def detect_vlr_timezone_from_url(
    fetch: Callable[[str], str],
    path: str = REFERENCE_MATCH_PATH,
) -> ZoneInfo | tzinfo:
    """Fetch a reference match page and detect the viewer timezone.

    Args:
        fetch: Callable accepting a URL path and returning HTML text.
        path: VLR.gg path of the reference match page.

    Returns:
        Detected timezone for the current viewer session.

    """
    html = HTMLParser(fetch(path))
    return detect_vlr_timezone(html)