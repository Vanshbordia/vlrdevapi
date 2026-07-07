"""Timezone detection for vlr.gg server-rendered content."""

from __future__ import annotations

import logging
import os
import re
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)

# VLR stores ``data-utc-ts`` timestamps in US Eastern time (not UTC).
VLR_STORED_TZ = ZoneInfo("America/New_York")

# Stable completed match used to detect the viewer timezone VLR.gg renders for.
REFERENCE_MATCH_PATH = "/670471/paper-rex-vs-leviat-n-valorant-masters-london-2026-gf"

_TIME_WITH_TZ_RE = re.compile(
    r"^(?P<time>\d{1,2}:\d{2}\s*(?:AM|PM))\s+(?P<tz>[A-Z]{2,5})$",
    re.IGNORECASE,
)

# Windows registry ``TimeZoneKeyName`` values mapped to IANA zones.
_WIN_TZ_TO_IANA: dict[str, str] = {
    "AUS Central Standard Time": "Australia/Darwin",
    "AUS Eastern Standard Time": "Australia/Sydney",
    "Afghanistan Standard Time": "Asia/Kabul",
    "Alaskan Standard Time": "America/Anchorage",
    "Arab Standard Time": "Asia/Riyadh",
    "Arabian Standard Time": "Asia/Dubai",
    "Arabic Standard Time": "Asia/Baghdad",
    "Argentina Standard Time": "America/Buenos_Aires",
    "Atlantic Standard Time": "America/Halifax",
    "Azerbaijan Standard Time": "Asia/Baku",
    "Bangladesh Standard Time": "Asia/Dhaka",
    "Belarus Standard Time": "Europe/Minsk",
    "Canada Central Standard Time": "America/Regina",
    "Cape Verde Standard Time": "Atlantic/Cape_Verde",
    "Caucasus Standard Time": "Asia/Yerevan",
    "Cen. Australia Standard Time": "Australia/Adelaide",
    "Central America Standard Time": "America/Guatemala",
    "Central Asia Standard Time": "Asia/Almaty",
    "Central Brazilian Standard Time": "America/Cuiaba",
    "Central Europe Standard Time": "Europe/Budapest",
    "Central European Standard Time": "Europe/Warsaw",
    "Central Pacific Standard Time": "Pacific/Guadalcanal",
    "Central Standard Time": "America/Chicago",
    "Central Standard Time (Mexico)": "America/Mexico_City",
    "China Standard Time": "Asia/Shanghai",
    "E. Africa Standard Time": "Africa/Nairobi",
    "E. Australia Standard Time": "Australia/Brisbane",
    "E. Europe Standard Time": "Europe/Chisinau",
    "E. South America Standard Time": "America/Sao_Paulo",
    "Eastern Standard Time": "America/New_York",
    "Egypt Standard Time": "Africa/Cairo",
    "Ekaterinburg Standard Time": "Asia/Yekaterinburg",
    "FLE Standard Time": "Europe/Kiev",
    "Fiji Standard Time": "Pacific/Fiji",
    "GMT Standard Time": "Europe/London",
    "Georgian Standard Time": "Asia/Tbilisi",
    "Greenland Standard Time": "America/Godthab",
    "Greenwich Standard Time": "Atlantic/Reykjavik",
    "GTB Standard Time": "Europe/Bucharest",
    "Hawaiian Standard Time": "Pacific/Honolulu",
    "India Standard Time": "Asia/Kolkata",
    "Iran Standard Time": "Asia/Tehran",
    "Israel Standard Time": "Asia/Jerusalem",
    "Jordan Standard Time": "Asia/Amman",
    "Kaliningrad Standard Time": "Europe/Kaliningrad",
    "Korea Standard Time": "Asia/Seoul",
    "Libya Standard Time": "Africa/Tripoli",
    "Line Islands Standard Time": "Pacific/Kiritimati",
    "Magadan Standard Time": "Asia/Magadan",
    "Mauritius Standard Time": "Indian/Mauritius",
    "Middle East Standard Time": "Asia/Beirut",
    "Montevideo Standard Time": "America/Montevideo",
    "Morocco Standard Time": "Africa/Casablanca",
    "Mountain Standard Time": "America/Denver",
    "Mountain Standard Time (Mexico)": "America/Chihuahua",
    "Myanmar Standard Time": "Asia/Yangon",
    "N. Central Asia Standard Time": "Asia/Novosibirsk",
    "Namibia Standard Time": "Africa/Windhoek",
    "Nepal Standard Time": "Asia/Katmandu",
    "New Zealand Standard Time": "Pacific/Auckland",
    "Newfoundland Standard Time": "America/St_Johns",
    "North Asia East Standard Time": "Asia/Irkutsk",
    "North Asia Standard Time": "Asia/Krasnoyarsk",
    "North Korea Standard Time": "Asia/Pyongyang",
    "Pacific SA Standard Time": "America/Santiago",
    "Pacific Standard Time": "America/Los_Angeles",
    "Pacific Standard Time (Mexico)": "America/Santa_Isabel",
    "Pakistan Standard Time": "Asia/Karachi",
    "Paraguay Standard Time": "America/Asuncion",
    "Romance Standard Time": "Europe/Paris",
    "Russia Time Zone 10": "Asia/Srednekolymsk",
    "Russia Time Zone 11": "Asia/Kamchatka",
    "Russia Time Zone 3": "Europe/Samara",
    "Russian Standard Time": "Europe/Moscow",
    "SA Eastern Standard Time": "America/Cayenne",
    "SA Pacific Standard Time": "America/Bogota",
    "SA Western Standard Time": "America/La_Paz",
    "SE Asia Standard Time": "Asia/Bangkok",
    "Samoa Standard Time": "Pacific/Apia",
    "Singapore Standard Time": "Asia/Singapore",
    "South Africa Standard Time": "Africa/Johannesburg",
    "Sri Lanka Standard Time": "Asia/Colombo",
    "Syria Standard Time": "Asia/Damascus",
    "Taipei Standard Time": "Asia/Taipei",
    "Tasmania Standard Time": "Australia/Hobart",
    "Tokyo Standard Time": "Asia/Tokyo",
    "Tonga Standard Time": "Pacific/Tongatapu",
    "Turkey Standard Time": "Europe/Istanbul",
    "US Eastern Standard Time": "America/Indianapolis",
    "US Mountain Standard Time": "America/Phoenix",
    "UTC": "UTC",
    "UTC+12": "Etc/GMT-12",
    "UTC-02": "Etc/GMT+2",
    "UTC-08": "Etc/GMT+8",
    "UTC-09": "Etc/GMT+9",
    "UTC-11": "Etc/GMT+11",
    "Ulaanbaatar Standard Time": "Asia/Ulaanbaatar",
    "Venezuela Standard Time": "America/Caracas",
    "Vladivostok Standard Time": "Asia/Vladivostok",
    "W. Australia Standard Time": "Australia/Perth",
    "W. Central Africa Standard Time": "Africa/Lagos",
    "W. Europe Standard Time": "Europe/Berlin",
    "West Asia Standard Time": "Asia/Tashkent",
    "West Pacific Standard Time": "Pacific/Port_Moresby",
    "Yakutsk Standard Time": "Asia/Yakutsk",
}


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


def _iana_from_tz_env() -> ZoneInfo | None:
    tz_name = os.environ.get("TZ")
    if not tz_name:
        return None
    tz_name = tz_name.removeprefix(":")
    if tz_name in {"", "UTC", "GMT"}:
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return None


def _iana_name_from_localtime_file() -> str | None:
    for candidate in (Path("/etc/localtime"), Path("/var/db/timezone/zoneinfo")):
        if not candidate.exists():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        parts = resolved.parts
        if "zoneinfo" not in parts:
            continue
        idx = parts.index("zoneinfo")
        name = "/".join(parts[idx + 1 :])
        if name:
            return name
    return None


def _iana_name_from_windows_registry() -> str | None:
    if sys.platform != "win32":
        return None
    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation",
        )
        win_tz, _ = winreg.QueryValueEx(key, "TimeZoneKeyName")
    except OSError:
        return None
    return _WIN_TZ_TO_IANA.get(win_tz)


def _system_iana_timezone() -> ZoneInfo:
    """Return a DST-aware named IANA timezone for the local system."""
    zone = _iana_from_tz_env()
    if zone is not None:
        return zone

    name = _iana_name_from_localtime_file() or _iana_name_from_windows_registry()
    if name is not None:
        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            logger.debug("Unknown IANA timezone %r from system config", name)

    logger.debug("Could not resolve system IANA timezone; falling back to UTC")
    return ZoneInfo("UTC")


def _detect_from_offset(
    stored_ts: str,
    displayed_time: str,
    displayed_date: str,
) -> timezone | None:
    """Infer viewer timezone by computing the offset between stored UTC and displayed local time."""
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
        local_date = canonical.date()
    else:
        local_date = local_date.replace(year=canonical.year)

    local_naive = datetime.combine(local_date, local_time)
    local_as_utc = local_naive.replace(tzinfo=UTC)
    offset = local_as_utc - canonical
    return timezone(offset)


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
        return _system_iana_timezone()

    ts_el = date_container.css_first(".moment-tz-convert[data-utc-ts]")
    time_el = date_container.css_first(
        ".moment-tz-convert[data-moment-format='h:mm A z']",
    )
    date_el = date_container.css_first(
        ".moment-tz-convert[data-moment-format='dddd, MMMM D']",
    )

    if time_el is None:
        logger.debug("No timezone-formatted time element found; using system timezone")
        return _system_iana_timezone()

    displayed_time = time_el.text(strip=True)
    if ts_el is not None and date_el is not None:
        stored_ts = ts_el.attributes.get("data-utc-ts", "") or ""
        zone = _detect_from_offset(stored_ts, displayed_time, date_el.text(strip=True))
        if zone is not None:
            return zone

    logger.debug("Could not detect VLR timezone from %r; using system timezone", displayed_time)
    return _system_iana_timezone()


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