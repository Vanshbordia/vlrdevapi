"""Helpers for deriving expected values from fixture HTML."""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.info.parser import _parse_date_range
from vlrdevapi._player._common_parsing import _parse_inactive_date, _parse_month_year, _parse_team_dates
from vlrdevapi.commons.datetime import date_to_utc_datetime, parse_vlr_date


def event_dates_text(html: HTMLParser) -> str:
    """Return the raw dates label value from an event overview page."""
    for child in html.css(".event-header-main-meta div, .event-meta div"):
        label = child.css_first(".label")
        value = child.css_first(".value")
        if label and value and label.text(strip=True).lower() == "dates":
            return value.text(strip=True)
    return ""


def expected_event_dates(html: HTMLParser):
    """Parse expected start/end datetimes from event fixture HTML."""
    start, end = _parse_date_range(event_dates_text(html))
    return start, end


def transaction_date_from_row(row: Node):
    """Parse expected transaction date from a table row's first cell."""
    tds = row.css("td")
    if not tds:
        return None
    parsed = parse_vlr_date(tds[0].text(strip=True))
    return date_to_utc_datetime(parsed) if parsed else None


def _parse_team_card(card: Node) -> dict[str, object]:
    joined = left = inactive = None
    for div in card.css("div.ge-text-light"):
        style = div.attributes.get("style", "") or ""
        raw = div.text(strip=True)
        if not raw:
            continue
        if "font-style: italic" in style or "font-style:italic" in style:
            inactive = _parse_inactive_date(raw)
        else:
            joined_part, left_part = _parse_team_dates(raw)
            if joined_part is not None or left_part is not None:
                joined, left = joined_part, left_part

    return {
        "joined_date": joined,
        "left_date": left,
        "inactive_date": inactive,
    }


def player_team_entries(html: HTMLParser, team_name: str) -> list[dict[str, object]]:
    """Extract all team history entries for a player team name."""
    entries: list[dict[str, object]] = []
    for anchor in html.css('a[href*="/team/"]'):
        name_el = anchor.css_first('div[style*="font-weight: 500"]')
        if name_el and name_el.text(strip=True) == team_name:
            entries.append(_parse_team_card(anchor))
    return entries


def player_team_dates(html: HTMLParser, team_name: str) -> dict[str, object]:
    """Extract expected team date fields from the first matching player team card."""
    entries = player_team_entries(html, team_name)
    return entries[0] if entries else {}


