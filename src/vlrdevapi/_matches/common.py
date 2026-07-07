"""Shared utilities for match enrichment and parsing across live/upcoming/completed modules."""

import logging
from collections.abc import Callable
from datetime import date, datetime, tzinfo
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import httpx
from selectolax.parser import HTMLParser, Node

from vlrdevapi._cache import LRUCache
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._utils.paths import team as team_path
from vlrdevapi._utils.team_parsing import _parse_team_basic
from vlrdevapi.commons.datetime import parse_vlr_datetime
from vlrdevapi.exceptions import VlrdevapiException
from vlrdevapi.fetcher import RetryConfig, fetch_sync

logger = logging.getLogger(__name__)

class MatchEntryProtocol(Protocol):
    match_id: int
    team1: Any
    team2: Any


# ---------------------------------------------------------------------------
# Date-header / pagination helpers
# ---------------------------------------------------------------------------


def parse_date_header(text: str) -> date | None:
    """Parse a date from a date-header label on the matches page.

    Strips leading labels such as "Today" or "Tomorrow" and attempts to
    parse the remaining ``<Month> <Day> <Year>`` format.

    Args:
        text: Raw text from a ``.wf-label.mod-large`` element.

    Returns:
        Parsed date, or ``None`` if parsing fails.

    """
    text = text.replace(",", "").replace("Today", "").replace("Tomorrow", "").strip()
    parts = text.split()
    if len(parts) >= 3:
        try:
            month_day_year = " ".join(parts[1:])
            return datetime.strptime(month_day_year, "%B %d %Y").date()
        except ValueError:
            pass
    return None


def check_pagination(html: HTMLParser) -> bool:
    """Check whether the page has pagination links to additional pages.

    Args:
        html: Parsed HTML document.

    Returns:
        ``True`` if at least one page link exists, ``False`` otherwise.

    """
    pagination_el = html.css_first("div.action-container-pages")
    if pagination_el:
        page_links = pagination_el.css("a.btn.mod-page")
        return len(page_links) > 0
    return False


# ---------------------------------------------------------------------------
# Generic match-card iteration (shared by completed/live/upcoming)
# ---------------------------------------------------------------------------


def parse_match_card_sync(
    card: Node,
    match_date: date,
    series_info_ns: SeriesInfoNamespace,
    client: httpx.Client,
    timeout: int,
    retry_config: RetryConfig,
    team_cache: LRUCache[int, dict[str, str]],
    parse_item: Callable,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> list:
    """Iterate match items inside a ``.wf-card`` and return parsed entries.

    For each match-anchor element the supplied ``parse_item`` callback is
    invoked; successfully parsed entries are enriched with team data and
    collected into a list.

    Args:
        card: The ``.wf-card`` DOM node containing match items.
        match_date: The date parsed from the preceding date header.
        series_info_ns: Namespace for fetching series info.
        client: Shared ``httpx.Client`` instance.
        timeout: Request timeout in seconds.
        retry_config: Retry configuration for HTTP requests.
        parse_item: Callable ``(Node, date) -> M | None`` that builds
            a concrete model (e.g. ``CompletedMatchEntry``).

    Returns:
        List of parsed match entries.

    """
    matches = []
    for match_item in card.css("a.match-item"):
        match = parse_item(match_item, match_date, source_tz=source_tz)
        if match and match.match_id > 0 and (match.team1 is not None or match.team2 is not None):
            enrich_team_data_sync(match, series_info_ns, client, timeout, retry_config, team_cache)
            matches.append(match)
    return matches


# ---------------------------------------------------------------------------
# Shared match-item field parsing
# ---------------------------------------------------------------------------


def parse_common_match_item_fields(
    item: Node,
    match_date: date,
    match: Any,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> bool:
    """Populate common fields shared across match entry types.

    Fills ``match_id``, ``url``, ``status``, ``event``, ``stage``, and
    ``datetime`` from the DOM node.

    Args:
        item: The ``a.match-item`` DOM node.
        match_date: The date parsed from the date header.
        match: A match entry model instance to populate in-place.

    Returns:
        ``True`` if parsing succeeded, ``False`` if both teams are TBD
        (caller should discard this entry).

    """
    href = item.attributes.get("href") or ""
    if href.startswith("/"):
        parts = href.strip("/").split("/")
        if len(parts) >= 1:
            match.match_id = int(parts[0])
    match.url = href

    time_el = item.css_first("div.match-item-time")
    time_text = time_el.text(strip=True) if time_el else None

    eta_el = item.css_first("div.match-item-eta div.ml")
    if eta_el:
        status_el = eta_el.css_first("div.ml-status")
        if status_el:
            match.status = status_el.text(strip=True).lower()

    event_el = item.css_first("div.match-item-event")
    if event_el:
        event_text = event_el.text(strip=True)
        series_el = event_el.css_first("div.match-item-event-series")
        if series_el:
            match.stage = series_el.text(strip=True)
            match.event = event_text.replace(match.stage, "").strip()

    if time_text:
        match.datetime = parse_vlr_datetime(match_date.strftime("%Y/%m/%d"), time_text, source_tz=source_tz)

    return True


# ---------------------------------------------------------------------------
# Team enrichment
# ---------------------------------------------------------------------------


def enrich_team_data_sync(
    match: MatchEntryProtocol,
    series_info_ns: SeriesInfoNamespace,
    client: httpx.Client,
    timeout: int,
    retry_config: RetryConfig,
    team_cache: LRUCache[int, dict[str, str]],
) -> None:
    """Fetch and attach team identifiers, names, and tags to a match entry.

    Team data is retrieved from the series-info endpoint and cached in an
    LRU cache to avoid redundant requests.

    Args:
        match: A match entry protocol instance with ``team1`` and ``team2``.
        series_info_ns: Namespace for fetching series info.
        client: Shared ``httpx.Client`` instance.
        timeout: Request timeout in seconds.
        retry_config: Retry configuration for HTTP requests.
        team_cache: Instance-level LRU cache for team data.

    Raises:
        VlrdevapiException: If team enrichment fails for any reason.

    """
    try:
        series_info = series_info_ns(match.match_id)
        team1_id = getattr(series_info.team1, "id", 0) if series_info.team1 else 0
        team2_id = getattr(series_info.team2, "id", 0) if series_info.team2 else 0

        for t_id, team_obj in [(team1_id, match.team1), (team2_id, match.team2)]:
            if t_id > 0 and team_obj is not None:
                cached = team_cache.get(t_id)
                if cached is not None:
                    team_obj.id = t_id
                    team_obj.name = cached["name"]
                    team_obj.tag = cached["tag"]
                else:
                    url = team_path(t_id)
                    html_parser = fetch_sync(client, url, timeout, retry_config=retry_config)
                    info = _parse_team_basic(html_parser)
                    team_obj.id = t_id
                    team_obj.name = info["name"]
                    team_obj.tag = info["tag"]
                    team_cache.put(t_id, info)
    except (VlrdevapiException, AttributeError, KeyError, TypeError, ValueError):
        logger.warning("Failed to enrich match %d with team data", match.match_id)
        raise



