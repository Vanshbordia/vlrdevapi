from selectolax.parser import HTMLParser, Node

from vlrdevapi._team.upcoming_matches.models import (
    TeamUpcomingMatchEntry,
    TeamUpcomingMatches,
)
from vlrdevapi.commons.datetime import parse_vlr_datetime
from vlrdevapi.fetcher import BASE_URL


def parse_team_upcoming_matches(
    html: HTMLParser,
    team_id: int,
) -> TeamUpcomingMatches:
    result = TeamUpcomingMatches(team_id=team_id)

    upcoming_h2 = None
    for h2 in html.css("h2.wf-label.mod-large"):
        h2_text = h2.text(strip=True).replace("\t", " ").replace("  ", " ")
        if "Upcoming matches" in h2_text:
            upcoming_h2 = h2
            break

    if not upcoming_h2:
        return result

    container = upcoming_h2.parent
    if not container:
        return result

    for item in container.css("a.wf-card.fc-flex.m-item"):
        match = _parse_match_item(item)
        if match and match.match_id > 0:
            result.matches.append(match)

    return result


def _parse_match_item(item: Node) -> TeamUpcomingMatchEntry | None:
    match = TeamUpcomingMatchEntry()

    href = item.attributes.get("href") or ""
    if href.startswith("/"):
        parts = href.strip("/").split("/")
        if parts and parts[0].isdigit():
            match.match_id = int(parts[0])
        match.url = f"{BASE_URL}{href}"
    else:
        match.url = href

    event_el = item.css_first(".m-item-event")
    if event_el:
        divs = event_el.css("div")
        if len(divs) >= 2:
            match.event = divs[1].text(strip=True)
        full_text = event_el.text(separator=" ", strip=True)
        if match.event and match.event in full_text:
            stage_text = full_text.replace(match.event, "").strip()
            match.stage = stage_text

    date_el = item.css_first(".m-item-date")
    if date_el:
        divs = date_el.css("div")
        if len(divs) >= 2:
            date_text = divs[1].text(strip=True)
        elif divs:
            date_text = divs[0].text(strip=True)
        else:
            date_text = ""
        time_text = ""
        for child in date_el.iter(include_text=True):
            if child.tag == "-text":
                txt = child.text(strip=True)
                if txt:
                    time_text = txt
                    break
        if date_text:
            match.datetime = parse_vlr_datetime(date_text, time_text)

    return match if match.match_id > 0 else None
