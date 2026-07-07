"""Parse completed matches from vlr.gg HTML pages."""

import logging
from datetime import date, tzinfo
from zoneinfo import ZoneInfo

import httpx
from selectolax.parser import HTMLParser, Node

from vlrdevapi._cache import LRUCache
from vlrdevapi._matches.common import (
    check_pagination,
    parse_common_match_item_fields,
    parse_date_header,
    parse_match_card_sync,
)
from vlrdevapi._matches.completed.models import (
    CompletedMatchEntry,
    CompletedMatchesPage,
    TeamInCompletedMatch,
)
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.fetcher import RetryConfig

logger = logging.getLogger(__name__)


def parse_completed_matches(
    html: HTMLParser,
    series_info_ns: SeriesInfoNamespace,
    client: httpx.Client,
    timeout: int,
    retry_config: RetryConfig,
    team_cache: LRUCache[int, dict[str, str]],
    source_tz: ZoneInfo | tzinfo | None = None,
) -> CompletedMatchesPage:
    """Parse the vlr.gg results page and extract completed match entries.

    Iterates over DOM elements to locate date headers and match cards,
    then parses each card into a ``CompletedMatchEntry``. Only entries
    with ``status == "completed"`` are included in the result.

    Args:
        html: Parsed HTML document.
        series_info_ns: Namespace for fetching series info.
        client: Shared ``httpx.Client`` instance.
        timeout: Request timeout in seconds.
        retry_config: Retry configuration for HTTP requests.

    Returns:
        CompletedMatchesPage: Container with a list of
            ``CompletedMatchEntry`` objects and a ``has_next_page`` flag.

    """
    matches = []
    current_date = None

    root = html.root
    if root is None:
        return CompletedMatchesPage(matches=[], has_next_page=False)

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
                team_cache, _parse_match_item, source_tz=source_tz,
            )
            matches.extend(card_matches)

    completed_matches = [match for match in matches if match.status == "completed"]
    has_next_page = check_pagination(html)
    return CompletedMatchesPage(matches=completed_matches, has_next_page=has_next_page)


def _parse_match_item(
    item: Node,
    match_date: date,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> CompletedMatchEntry | None:
    """Parse a single completed match item from a match-card anchor.

    Args:
        item: The ``a.match-item`` DOM node.
        match_date: The date parsed from the date header.

    Returns:
        A ``CompletedMatchEntry`` if parsing succeeds and at least one
        team is not TBD, or ``None`` if parsing fails.

    """
    try:
        match = CompletedMatchEntry()

        team_els = item.css("div.match-item-vs-team")
        if len(team_els) >= 2:
            team1_parsed = _parse_team_with_score(team_els[0])
            team2_parsed = _parse_team_with_score(team_els[1])
            match.team1 = None if team1_parsed.name == "TBD" else team1_parsed
            match.team2 = None if team2_parsed.name == "TBD" else team2_parsed
            if match.team1 is None and match.team2 is None:
                return None

        parse_common_match_item_fields(item, match_date, match, source_tz=source_tz)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        logger.debug("Failed to parse completed match item", exc_info=True)
        return None
    else:
        return match


def _parse_team_with_score(team_el: Node) -> TeamInCompletedMatch:
    """Extract team name, country, score, and winner status from a match-item element.

    Args:
        team_el: The ``div.match-item-vs-team`` DOM node.

    Returns:
        TeamInCompletedMatch: Populated with name, country, score, and
            ``is_winner`` flag.

    """
    team = TeamInCompletedMatch()
    name_el = team_el.css_first("div.match-item-vs-team-name div.text-of")
    if name_el:
        team.name = name_el.text(strip=True)
        flag_el = name_el.css_first("span.flag")
        if flag_el:
            for cls in (flag_el.attributes.get("class") or "").split():
                if cls.startswith("mod-"):
                    team.country_name = get_country_name(cls[4:])
                    break

    classes = (team_el.attributes.get("class") or "").split()
    team.is_winner = "mod-winner" in classes

    score_el = team_el.css_first("div.match-item-vs-team-score")
    if score_el:
        try:
            team.score = int(score_el.text(strip=True))
        except ValueError:
            team.score = 0

    return team
