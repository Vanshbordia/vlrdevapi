"""Raw text extraction from fixture HTML.

These helpers only read visible strings from HTML. Expected datetimes are
built separately in ``tests.helpers.expected_from_html``.
"""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node


def event_dates_text(html: HTMLParser) -> str:
    """Return the raw dates label value from an event overview page."""
    for child in html.css(".event-header-main-meta div, .event-meta div"):
        label = child.css_first(".label")
        value = child.css_first(".value")
        if label and value and label.text(strip=True).lower() == "dates":
            return value.text(strip=True)
    return ""


def transaction_date_text(row: Node) -> str:
    """Return the raw date string from a transaction table row."""
    tds = row.css("td")
    if not tds:
        return ""
    return tds[0].text(strip=True)


def player_team_texts(html: HTMLParser, team_name: str) -> list[list[str]]:
    """Return raw date strings for each team card matching ``team_name``."""
    entries: list[list[str]] = []
    for anchor in html.css('a[href*="/team/"]'):
        name_el = anchor.css_first('div[style*="font-weight: 500"]')
        if name_el and name_el.text(strip=True) == team_name:
            lines = [
                div.text(strip=True)
                for div in anchor.css("div.ge-text-light")
                if div.text(strip=True)
            ]
            entries.append(lines)
    return entries


