
import re

from selectolax.parser import HTMLParser, Node

from vlrdevapi._team.placements.models import (
    EventPlacement,
    TeamEventPlacement,
    TeamPlacements,
)
from vlrdevapi.commons.prizes import parse_prize_amount


def parse_team_placements(html: HTMLParser, team_id: int) -> TeamPlacements:
    """Parse team placements from team page HTML.

    Args:
        html: Parsed HTML of the team page.
        team_id: The team identifier.

    Returns:
        TeamPlacements: Parsed placements with event history and total winnings.

    """
    result = TeamPlacements(team_id=team_id)

    placements_h2 = None
    for h2 in html.css("h2.wf-label.mod-large"):
        h2_text = h2.text(strip=True)
        if "Event Placements" in h2_text:
            placements_h2 = h2
            break

    if not placements_h2:
        return result

    card = placements_h2.next
    while card and not (
        card.tag == "div" and "wf-card" in (card.attributes.get("class") or "")
    ):
        card = card.next

    if not card:
        return result

    total_winnings_div = card.css_first("div[style*='padding']")
    if total_winnings_div:
        label_el = total_winnings_div.css_first(".wf-module-label")
        if label_el and "Total Winnings" in label_el.text(strip=True):
            span_el = total_winnings_div.css_first("span[style*='font-size']")
            if span_el:
                winnings_text = span_el.text(strip=True)
                value, currency = parse_prize_amount(winnings_text)
                result.total_winnings = value
                result.total_winnings_currency = currency

    for event_link in card.css("a.team-event-item"):
        event_placement = _parse_event_item(event_link)
        if event_placement and event_placement.event_id > 0:
            result.placements.append(event_placement)

    return result


def _parse_event_item(item: Node) -> TeamEventPlacement | None:
    """Parse a single event placement item.

    Args:
        item: The event item HTML node.

    Returns:
        TeamEventPlacement | None: The parsed event placement, or ``None``
        if the event ID could not be determined.

    """
    event = TeamEventPlacement()

    href = item.attributes.get("href") or ""
    if href.startswith("/event/"):
        parts = href.strip("/").split("/")
        if len(parts) >= 2 and parts[1].isdigit():
            event.event_id = int(parts[1])

    name_el = item.css_first(".text-of")
    if name_el:
        event.event_name = name_el.text(strip=True)

    year_divs = item.css("div")
    for div in year_divs:
        div_text = div.text(strip=True)
        if div_text and re.match(r"^\d{4}$", div_text):
            event.year = int(div_text)
            break

    series_spans = item.css(".team-event-item-series")
    for series_span in series_spans:
        placement = _parse_series_span(series_span)
        if placement:
            event.placements.append(placement)

    prize_el = item.css_first("span[style*='font-weight: 700']")
    if prize_el:
        prize_text = prize_el.text(strip=True)
        value, currency = parse_prize_amount(prize_text)
        event.prize = value
        event.prize_currency = currency

    return event if event.event_id > 0 else None


def _parse_series_span(span: Node) -> EventPlacement | None:
    """Parse a series span for stage and placement.

    Args:
        span: The series span HTML node.

    Returns:
        EventPlacement | None: The parsed placement with stage and rank,
        or ``None`` if the span text is empty.

    """
    text = span.text(strip=True)
    if not text:
        return None

    placement = EventPlacement()

    if "–" in text:  # noqa: RUF001
        parts = text.split("–", 1)  # noqa: RUF001
        placement.stage = parts[0].strip()
        placement.placement = parts[1].strip()
    elif "-" in text:
        parts = text.split("-", 1)
        placement.stage = parts[0].strip()
        placement.placement = parts[1].strip()
    else:
        placement.placement = text

    return placement



def _parse_prize(text: str) -> tuple[int | None, str | None]:
    """Parse prize text into (value, currency) tuple.

    Args:
        text: Prize text string (e.g., ``"$125,000"``).

    Returns:
        tuple[int | None, str | None]: A pair ``(value, currency)``
        where ``value`` is the numeric amount and ``currency`` is the
        symbol, or ``(None, None)`` if the text is empty.

    Examples:
        >>> _parse_prize("$125,000")
        (125000, '$')
        >>> _parse_prize("")
        (None, None)

    """
    if not text:
        return None, None

    currency_match = re.match(r"^([^\d]+)", text)
    currency = currency_match.group(1) if currency_match else None

    value_match = re.search(r"[\d,]+", text)
    if value_match:
        value_str = value_match.group().replace(",", "")
        try:
            value = int(value_str)
        except ValueError:
            pass
        else:
            return value, currency

    return None, currency or None
