from selectolax.parser import HTMLParser, Node

from vlrdevapi._team.completed_matches.models import (
    TeamCompletedMatchEntry,
    TeamCompletedMatches,
)
from vlrdevapi.commons.datetime import parse_vlr_datetime
from vlrdevapi.fetcher import BASE_URL


def parse_team_completed_matches(
    html: HTMLParser,
    team_id: int,
) -> TeamCompletedMatches:
    result = TeamCompletedMatches(team_id=team_id)
    for item in html.css("a.wf-card.fc-flex.m-item"):
        match = _parse_match_item(item, team_id)
        if match and match.match_id > 0:
            result.matches.append(match)
    return result


def _parse_match_item(item: Node, team_id: int) -> TeamCompletedMatchEntry | None:
    match = TeamCompletedMatchEntry()

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

    result_el = item.css_first(".m-item-result")
    if result_el:
        spans = result_el.css("span")
        if len(spans) >= 2:
            try:
                match.team_score = int(spans[0].text(strip=True))
                match.opponent_score = int(spans[-1].text(strip=True))
            except ValueError:
                pass
        match.is_win = match.team_score > match.opponent_score
        classes = (result_el.attributes.get("class") or "").split()
        if "mod-win" in classes:
            match.is_win = True
        elif "mod-loss" in classes:
            match.is_win = False

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
