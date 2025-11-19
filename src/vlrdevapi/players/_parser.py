"""Shared parsing utilities for players (private module)."""

from __future__ import annotations

import datetime
import re

from ..utils import parse_int, parse_float

_MONTH_YEAR_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
    re.IGNORECASE,
)

_USAGE_RE = re.compile(r"\((\d+)\)\s*(\d+)%")


def _parse_month_year(text: str) -> datetime.date | None:
    """Parse month-year format to date."""
    match = _MONTH_YEAR_RE.search(text)
    if not match:
        return None
    month_name, year_str = match.groups()
    try:
        month = datetime.datetime.strptime(month_name.title(), "%B").month
        return datetime.date(int(year_str), month, 1)
    except ValueError:
        return None


def _parse_usage(text: str | None) -> tuple[int | None, float | None]:
    """Parse usage text like '(10) 50%'."""
    if not text:
        return None, None
    match = _USAGE_RE.search(text)
    if match:
        count = parse_int(match.group(1))
        percent = parse_float(match.group(2))
        return count, percent / 100.0 if percent is not None else None
    return None, None
