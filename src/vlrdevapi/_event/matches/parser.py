
from datetime import date

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.matches.models import (
    EventMatch,
    EventMatches,
    MatchStatus,
    MatchTeam,
)
from vlrdevapi.commons.datetime import (
    parse_vlr_date,
    parse_vlr_datetime,
    parse_vlr_time,
)
import contextlib


def parse_event_matches(
    html: HTMLParser,
    event_id: int,
) -> EventMatches:
    """Parse event matches from the matches page HTML.

    Args:
        html: Parsed HTML from the event matches page.
        event_id: Unique event identifier on vlr.gg.

    Returns:
        EventMatches containing a list of parsed EventMatch objects.

    """
    matches: list[EventMatch] = []
    current_date: date | None = None

    date_labels = html.css("div.wf-label.mod-large")
    for date_label in date_labels:
        date_text = date_label.text(deep=False, strip=True)
        current_date = parse_vlr_date(date_text)

        card = _find_next_wf_card(date_label)
        if not card:
            continue

        for match_link in card.css("a.match-item"):
            match = _parse_match_item(match_link, event_id, current_date)
            if match:
                matches.append(match)

    return EventMatches(event_id=event_id, matches=matches)


def _find_next_wf_card(node: Node) -> Node | None:
    """Find the next sibling div with class 'wf-card'.

    Args:
        node: Starting node whose next siblings are searched.

    Returns:
        The next wf-card div, or None if not found.

    """
    sibling = node.next
    while sibling:
        if sibling.tag == "div":
            class_attr = sibling.attributes.get("class") or ""
            if "wf-card" in class_attr:
                return sibling
        sibling = sibling.next
    return None


def _parse_match_item(
    match_link: Node, event_id: int, match_date: date | None,
) -> EventMatch | None:
    """Parse a single match-item anchor into an EventMatch.

    Args:
        match_link: The a.match-item node.
        event_id: Event identifier for the match.
        match_date: Date parsed from the parent section label.

    Returns:
        EventMatch or None if the match ID cannot be extracted.

    """
    href = match_link.attributes.get("href", "")
    if not href:
        return None
    match_id = _extract_match_id(href)
    if not match_id:
        return None

    time_el = match_link.css_first(".match-item-time")
    time_text = time_el.text(strip=True) if time_el else ""
    match_time = parse_vlr_time(time_text) if time_text else None

    teams: list[MatchTeam] = []
    for team_el in match_link.css(".match-item-vs-team"):
        team = _parse_match_team(team_el)
        if team:
            teams.append(team)

    status = _parse_match_status(match_link)
    stage, phase = _parse_match_stage_phase(match_link)

    datetime_utc = None
    if match_date and match_time:
        datetime_utc = parse_vlr_datetime(
            match_date.strftime("%Y-%m-%d"),
            match_time.strftime("%I:%M %p"),
        )

    return EventMatch(
        event_id=event_id,
        match_id=match_id,
        stage=stage,
        phase=phase,
        status=status,
        match_date=match_date,
        match_time=match_time,
        datetime_utc=datetime_utc,
        teams=teams,
    )


def _extract_match_id(href: str) -> int | None:
    """Extract the numeric match ID from a match URL path.

    Args:
        href: URL path starting with the match ID (e.g. '12345/fnatic-vs-sentinels').

    Returns:
        Match ID integer, or None if extraction fails.

    """
    if not href:
        return None
    parts = href.strip("/").split("/")
    if parts:
        try:
            return int(parts[0])
        except ValueError:
            pass
    return None


def _parse_match_team(team_el: Node) -> MatchTeam | None:
    """Parse a single team element from a match item.

    Args:
        team_el: The .match-item-vs-team node.

    Returns:
        MatchTeam with name, score, and winner flag; None for invalid data.

    """
    class_attr = team_el.attributes.get("class") or ""
    winner = "mod-winner" in class_attr

    name_el = team_el.css_first(".match-item-vs-team-name .text-of")
    name = name_el.text(strip=True) if name_el else ""

    if name.upper() == "TBD":
        return MatchTeam(id=None, name="TBD", score=None, winner=False)

    score_el = team_el.css_first(".match-item-vs-team-score")
    score: int | None = None
    if score_el:
        score_text = score_el.text(strip=True)
        if score_text and score_text not in ("\u2013", "\u2014", "-"):
            with contextlib.suppress(ValueError):
                score = int(score_text)

    return MatchTeam(id=None, name=name, score=score, winner=winner)


def _parse_match_status(match_link: Node) -> MatchStatus:
    """Parse match status from the eta element.

    Checks for mod-live, mod-completed classes and status text.

    Args:
        match_link: The match-item anchor node.

    Returns:
        MatchStatus: 'live', 'completed', or 'upcoming'.

    """
    eta_el = match_link.css_first(".match-item-eta")
    if not eta_el:
        return MatchStatus("upcoming")

    ml_el = eta_el.css_first(".ml")
    if ml_el:
        ml_class = ml_el.attributes.get("class") or ""
        if "mod-live" in ml_class:
            return MatchStatus("live")
        if "mod-completed" in ml_class:
            return MatchStatus("completed")

    status_el = eta_el.css_first(".ml-status")
    if status_el:
        status_text = status_el.text(strip=True).lower()
        if "live" in status_text:
            return MatchStatus("live")
        if "completed" in status_text:
            return MatchStatus("completed")

    return MatchStatus("upcoming")


def _parse_match_stage_phase(match_link: Node) -> tuple[str, str]:
    """Parse stage and phase from the match-item-event element.

    Args:
        match_link: The match-item anchor node.

    Returns:
        (stage, phase) tuple; both are empty strings if not found.

    """
    event_el = match_link.css_first(".match-item-event")
    if not event_el:
        return "", ""

    phase_el = event_el.css_first(".match-item-event-series")
    phase = phase_el.text(strip=True) if phase_el else ""

    full_text = event_el.text(strip=True)
    stage = full_text
    if phase and phase in full_text:
        stage = full_text.replace(phase, "").strip()

    return stage, phase
