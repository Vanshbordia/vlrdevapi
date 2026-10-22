from datetime import tzinfo
from zoneinfo import ZoneInfo

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._team.completed_matches.models import (
    TeamCompletedMatchEntry,
    TeamCompletedMatches,
)
from vlrdevapi._utils.pagination import check_pagination
from vlrdevapi._utils.text import normalize_whitespace, split_stage_bracket
from vlrdevapi.commons.datetime import parse_vlr_datetime
from vlrdevapi.fetcher import BASE_URL


def parse_team_completed_matches(
    html: HTMLParser,
    team_id: int,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> TeamCompletedMatches:
    result = TeamCompletedMatches(
        team_id=team_id,
        has_next_page=check_pagination(html),
    )
    for item in html.css("a.wf-card.fc-flex.m-item"):
        match = _parse_match_item(item, team_id, source_tz=source_tz)
        if match and match.match_id > 0:
            result.matches.append(match)
    return result


def _parse_match_item(item: Node, team_id: int, source_tz: ZoneInfo | tzinfo | None = None) -> TeamCompletedMatchEntry | None:
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
        name_el = event_el.css_first('div[style*="font-weight: 700"]')
        if name_el is None:
            # Older cards may not carry the inline style; the event name is
            # still the first inner div.
            divs = event_el.css("div")
            name_el = divs[1] if len(divs) >= 2 else None
        if name_el is not None:
            match.event = normalize_whitespace(name_el.text(strip=True))

        if match.event:
            full_text = normalize_whitespace(
                event_el.text(separator=" ", strip=True),
            )
            remaining = full_text.removeprefix(match.event).strip()
            match.stage, match.bracket = split_stage_bracket(remaining)

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
            match.datetime = parse_vlr_datetime(date_text, time_text, source_tz=source_tz)

    return match if match.match_id > 0 else None
