"""Parse upcoming matches from vlr.gg HTML pages."""

import logging
from datetime import date

import httpx
from selectolax.parser import HTMLParser, Node

from vlrdevapi._cache import LRUCache
from vlrdevapi._matches.common import (
    check_pagination,
    parse_common_match_item_fields,
    parse_date_header,
    parse_match_card_sync,
)
from vlrdevapi._matches.upcoming.models import (
    TeamInUpcomingMatch,
    UpcomingMatchEntry,
    UpcomingMatchesPage,
)
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.fetcher import RetryConfig

logger = logging.getLogger(__name__)


def parse_upcoming_matches(
    html: HTMLParser,
    series_info_ns: SeriesInfoNamespace,
    client: httpx.Client,
    timeout: int,
    retry_config: RetryConfig,
    team_cache: LRUCache[int, dict[str, str]],
) -> UpcomingMatchesPage:
    """Parse the vlr.gg matches page and extract upcoming match entries.

    Iterates over DOM elements to locate date headers and match cards,
    then parses each card into an ``UpcomingMatchEntry``. Only entries
    with ``status == "upcoming"`` are included in the result.

    Args:
        html: Parsed HTML document.
        series_info_ns: Namespace for fetching series info.
        client: Shared ``httpx.Client`` instance.
        timeout: Request timeout in seconds.
        retry_config: Retry configuration for HTTP requests.

    Returns:
        UpcomingMatchesPage: Container with a list of
            ``UpcomingMatchEntry`` objects and a ``has_next_page`` flag.

    """
    matches = []
    current_date = None

    root = html.root
    if root is None:
        return UpcomingMatchesPage(matches=[], has_next_page=False)

    for element in root.traverse():
        if element.tag is None or element.tag.lower() != "div":
            continue
        classes = (element.attributes.get("class") or "").split()
        if "wf-label" in classes and "mod-large" in classes:
            d = parse_date_header(element.text(strip=True))
            if d:
                current_date = d
        elif "wf-card" in classes and "mod-header" not in classes and current_date is not None:
            card_matches = parse_match_card_sync(
                element, current_date, series_info_ns, client, timeout, retry_config,
                team_cache, _parse_match_item,
            )
            matches.extend(card_matches)

    upcoming_matches = [match for match in matches if match.status == "upcoming"]
    has_next_page = check_pagination(html)
    return UpcomingMatchesPage(matches=upcoming_matches, has_next_page=has_next_page)


def _parse_match_item(
    item: Node,
    match_date: date,
) -> UpcomingMatchEntry | None:
    """Parse a single upcoming match item from a match-card anchor.

    Args:
        item: The ``a.match-item`` DOM node.
        match_date: The date parsed from the date header.

    Returns:
        An ``UpcomingMatchEntry`` if parsing succeeds and at least one
        team is not TBD, or ``None`` if parsing fails.

    """
    try:
        match = UpcomingMatchEntry()

        team_els = item.css("div.match-item-vs-team")
        if len(team_els) >= 2:
            team1_parsed = _parse_team_basic(team_els[0])
            team2_parsed = _parse_team_basic(team_els[1])
            match.team1 = None if team1_parsed.name == "TBD" else team1_parsed
            match.team2 = None if team2_parsed.name == "TBD" else team2_parsed
            if match.team1 is None and match.team2 is None:
                return None

        parse_common_match_item_fields(item, match_date, match)

        eta_el = item.css_first("div.match-item-eta div.ml")
        if eta_el:
            eta_el_inner = eta_el.css_first("div.ml-eta")
            if eta_el_inner:
                match.eta = eta_el_inner.text(strip=True)

    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        logger.debug("Failed to parse upcoming match item", exc_info=True)
        return None
    else:
        return match


def _parse_team_basic(team_el: Node) -> TeamInUpcomingMatch:
    """Extract team name and country from a ``.match-item-vs-team`` element.

    Args:
        team_el: The ``div.match-item-vs-team`` DOM node.

    Returns:
        TeamInUpcomingMatch: Populated with name and country.

    """
    team = TeamInUpcomingMatch()
    name_el = team_el.css_first("div.match-item-vs-team-name div.text-of")
    if name_el:
        team.name = name_el.text(strip=True)
        flag_el = name_el.css_first("span.flag")
        if flag_el:
            for cls in (flag_el.attributes.get("class") or "").split():
                if cls.startswith("mod-"):
                    team.country_name = get_country_name(cls[4:])
                    break
    return team
