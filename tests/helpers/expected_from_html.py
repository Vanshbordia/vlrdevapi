"""Test-only expected value builders from raw fixture strings.

Intentionally separate from ``vlrdevapi`` parsers so tests can catch parser
regressions without circular imports.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

UTC = timezone.utc

_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

_MONTH_YEAR_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
    re.IGNORECASE,
)
_DASHES = "\u2013\u2014\u2212-"


def _utc(year: int, month: int, day: int = 1) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


def _parse_month_day_year(text: str, default_year: int | None = None) -> datetime | None:
    text = text.strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"):
        try:
            parsed = datetime.strptime(text, fmt)
            return _utc(parsed.year, parsed.month, parsed.day)
        except ValueError:
            continue

    match = re.match(r"^(\d{1,2}),?\s*(\d{4})$", text)
    if match and default_year is not None:
        month_match = re.match(r"^([A-Za-z]+)", text)
        return None

    match = re.match(r"^([A-Za-z]+)\s+(\d{1,2})$", text)
    if match and default_year is not None:
        for fmt in ("%b %d", "%B %d"):
            try:
                parsed = datetime.strptime(f"{match.group(1)} {match.group(2)}", fmt)
                return _utc(default_year, parsed.month, parsed.day)
            except ValueError:
                continue

    match = re.match(r"^(\d{1,2}),?\s*(\d{4})$", text)
    if match:
        return None

    return None


def month_year_label(text: str) -> datetime | None:
    match = _MONTH_YEAR_RE.search(text.strip())
    if not match:
        return None
    month = _MONTHS[match.group(1).lower()]
    return _utc(int(match.group(2)), month)


def player_team_dates_from_lines(lines: list[str]) -> dict[str, datetime | None]:
    joined = left = inactive = None
    for line in lines:
        lower = line.lower()
        if lower.startswith("inactive from "):
            inactive = month_year_label(line)
            continue
        if lower.startswith("joined in "):
            joined = month_year_label(line)
            continue
        if lower.startswith("left in "):
            left = month_year_label(line)
            continue
        parts = re.split(f"[{_DASHES}]", line)
        if len(parts) == 2:
            joined = month_year_label(parts[0])
            left = month_year_label(parts[1])
    return {"joined_date": joined, "left_date": left, "inactive_date": inactive}


def transaction_date_label(text: str) -> datetime | None:
    text = text.strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            return _utc(parsed.year, parsed.month, parsed.day)
        except ValueError:
            continue
    return None


def event_dates_label(text: str) -> tuple[datetime | None, datetime | None]:
    text = text.strip()
    if not text:
        return None, None

    separator = None
    for sep in [" – ", " - ", "–", "-"]:
        if sep in text:
            separator = sep
            break

    if separator is None:
        single = _parse_month_day_year(text)
        return single, single

    left, right = (part.strip() for part in text.split(separator, 1))
    end = _parse_month_day_year(right)
    if end is None:
        day_year = re.match(r"^(\d{1,2}),?\s*(\d{4})$", right)
        month_day = re.match(r"^([A-Za-z]+)\s+(\d{1,2})", left)
        if day_year and month_day:
            for fmt in ("%b", "%B"):
                try:
                    month = datetime.strptime(month_day.group(1), fmt).month
                    end = _utc(int(day_year.group(2)), month, int(day_year.group(1)))
                    break
                except ValueError:
                    continue
    if end is None:
        return None, None

    start = _parse_month_day_year(left)
    if start is None:
        start = _parse_month_day_year(left, default_year=end.year)
    return start, end