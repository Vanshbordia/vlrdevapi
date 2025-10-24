"""Common utility functions for parsing HTML and data extraction."""

import datetime
import unicodedata
import re
from functools import lru_cache
from urllib import parse

from bs4 import Tag

from .config import get_config

_config = get_config()

# Pre-compiled regex patterns for performance
_WHITESPACE_RE = re.compile(r"\s+")
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
_ALPHANUMERIC_RE = re.compile(r"[^a-z0-9]")
_DATE_SPLIT_RE = re.compile(r"\s*-\s*")
_MONTH_DAY_RE = re.compile(r"^(?P<month>\w+)\s+(?P<day>\d{1,2})(?:,\s*(?P<year>\d{4}))?$")
_DAY_ONLY_RE = re.compile(r"^\d{1,2}$")
_DAY_YEAR_RE = re.compile(r"^\d{1,2},\s*\d{4}$")


def extract_text(element: Tag | None) -> str:
    """Extract text from a BeautifulSoup element (normalized to NFC)."""
    if not element:
        return ""
    raw = element.get_text(strip=True)
    # Normalize to NFC to ensure symbols (e.g., infinity) are consistent across platforms
    try:
        return unicodedata.normalize("NFC", raw)
    except Exception:
        return raw


@lru_cache(maxsize=512)
def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def absolute_url(url: str | None) -> str | None:
    """Convert relative URL to absolute URL."""
    if not url:
        return None
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("http"):
        return url
    return parse.urljoin(f"{_config.vlr_base}/", url.lstrip("/"))


def parse_int(text: str | None) -> int | None:
    """Parse integer from text, returning None if invalid."""
    if text is None:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError:
        return None


@lru_cache(maxsize=256)
def parse_float(text: str | None) -> float | None:
    """Parse float from text, returning None if invalid."""
    if text is None:
        return None
    # Extract first number from text
    match = _NUMBER_RE.search(text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_percent(text: str | None) -> float | None:
    """Parse percentage from text, returning as decimal (0-1)."""
    if text is None:
        return None
    numeric = parse_float(text)
    if numeric is None:
        return None
    # If text contains %, always divide by 100
    if "%" in text:
        return numeric / 100.0
    # If numeric > 1, assume it's a percentage and convert
    if numeric > 1:
        return numeric / 100.0
    return numeric


def extract_id_from_url(url: str | None, prefix: str) -> int | None:
    """
    Extract ID from URL path.
    
    Args:
        url: URL or path like '/team/123/name' or 'https://vlr.gg/team/123/name'
        prefix: Expected prefix like 'team', 'player', 'event'
    
    Returns:
        Extracted ID or None
    """
    if not url:
        return None
    try:
        parts = url.strip("/").split("/")
        # Handle both full URLs and relative paths
        for i, part in enumerate(parts):
            if part == prefix and i + 1 < len(parts) and parts[i + 1].isdigit():
                return int(parts[i + 1])
    except Exception:
        pass
    return None


def extract_match_id(href: str | None) -> int | None:
    """Extract match ID from href (format: /12345/slug)."""
    if not href:
        return None
    try:
        parts = href.strip("/").split("/")
        return int(parts[0]) if parts and parts[0].isdigit() else None
    except Exception:
        return None


def extract_country_code(element: Tag | None) -> str | None:
    """Extract country code from flag element."""
    if not element:
        return None
    flag = element.select_one(".flag")
    if not flag:
        return None
    classes_val = flag.get("class")
    classes: list[str] = [c for c in classes_val if isinstance(c, str)] if isinstance(classes_val, (list, tuple)) else []
    for cls in classes:
        if cls.startswith("mod-") and cls != "mod-dark":
            return cls.removeprefix("mod-")
    return None


def parse_date(text: str, formats: list[str]) -> datetime.date | None:
    """
    Try to parse date from text using multiple formats.
    
    Args:
        text: Date string
        formats: List of strptime format strings to try
    
    Returns:
        Parsed date or None
    """
    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_time(text: str, formats: list[str]) -> datetime.time | None:
    """
    Try to parse time from text using multiple formats.
    
    Args:
        text: Time string
        formats: List of strptime format strings to try
    
    Returns:
        Parsed time or None
    """
    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def split_date_range(text: str | None) -> tuple[str | None, str | None]:
    """
    Split date range text into start and end parts.
    
    Examples:
        "Jan 2 - 5, 2025" -> ("Jan 2, 2025", "Jan 5, 2025")
        "Feb 8, 2025 - Mar 1, 2025" -> ("Feb 8, 2025", "Mar 1, 2025")
    """
    if not text:
        return None, None
    
    normalized = text.replace("—", "-").replace("–", "-").strip()
    parts = _DATE_SPLIT_RE.split(normalized, maxsplit=1)
    
    if not parts:
        return None, None
    
    start_raw = parts[0].strip() or None
    end_raw = parts[1].strip() if len(parts) > 1 else None
    
    if not start_raw:
        return None, end_raw
    
    # If end part lacks month, borrow from start
    month_match = _MONTH_DAY_RE.match(start_raw)
    if end_raw and month_match:
        month = month_match.group("month")
        year = month_match.group("year")
        if _DAY_ONLY_RE.match(end_raw):
            end_raw = f"{month} {end_raw}"
            if year:
                end_raw = f"{end_raw}, {year}"
        elif _DAY_YEAR_RE.match(end_raw):
            end_raw = f"{month} {end_raw}"
    
    return start_raw, end_raw


@lru_cache(maxsize=256)
def normalize_name(name: str) -> str:
    """Normalize name for comparison (lowercase, alphanumeric only)."""
    return _ALPHANUMERIC_RE.sub("", name.lower())
