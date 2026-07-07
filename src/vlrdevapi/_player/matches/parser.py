
from datetime import tzinfo
from zoneinfo import ZoneInfo

from selectolax.parser import HTMLParser, Node

from vlrdevapi._player.matches.models import MatchEntry, MatchHistoryPage, TeamInMatch
from vlrdevapi.commons.datetime import (
    parse_vlr_date,
    parse_vlr_datetime,
    parse_vlr_time,
)
import contextlib

_SDOT = "\u22c5"


def _split_stage_bracket(text: str) -> tuple[str, str]:
    text = text.strip()
    if _SDOT in text:
        parts = text.split(_SDOT, 1)
        stage = parts[0].strip()
        bracket = parts[1].strip() if len(parts) > 1 else ""
        return stage, bracket
    return "", text


def _parse_team(team_el: Node | None) -> TeamInMatch:
    team = TeamInMatch()
    if team_el is None:
        return team

    name_el = team_el.css_first(".m-item-team-name")
    if name_el:
        team.name = name_el.text(strip=True)

    tag_el = team_el.css_first(".m-item-team-tag")
    if tag_el:
        team.tag = tag_el.text(strip=True)

    return team


def _parse_match_item(a: Node, source_tz: ZoneInfo | tzinfo | None = None) -> MatchEntry:
    entry = MatchEntry()

    href = a.attributes.get("href", "") or ""
    entry.url = href
    parts = href.strip("/").split("/")
    if parts:
        with contextlib.suppress(ValueError):
            entry.match_id = int(parts[0])

    event_el = a.css_first(".m-item-event")
    if event_el:
        name_el = event_el.css_first('div[style*="font-weight: 700"]')
        if name_el:
            entry.event = name_el.text(strip=True)
        remaining = event_el.text(strip=True)
        if entry.event and remaining.startswith(entry.event):
            remaining = remaining[len(entry.event) :].strip()
        stage, bracket = _split_stage_bracket(remaining)
        entry.stage = stage
        entry.bracket = bracket

    team1_el = a.css_first(".m-item-team:not(.mod-right)")
    team2_el = a.css_first(".m-item-team.mod-right")
    entry.team1 = _parse_team(team1_el)
    entry.team2 = _parse_team(team2_el)

    result_el = a.css_first(".m-item-result")
    if result_el:
        classes = result_el.attributes.get("class", "") or ""
        if "mod-win" in classes:
            entry.result = "win"
        elif "mod-loss" in classes:
            entry.result = "loss"

        spans = result_el.css("span")
        if len(spans) >= 2:
            with contextlib.suppress(ValueError):
                entry.score1 = int(spans[0].text(strip=True))
            with contextlib.suppress(ValueError):
                entry.score2 = int(spans[1].text(strip=True))

    date_el = a.css_first(".m-item-date")
    if date_el:
        date_text = ""
        time_text = ""
        divs = date_el.css("div")
        if len(divs) >= 2:
            date_text = divs[1].text(strip=True)
        node = divs[1].next if len(divs) >= 2 else None
        while node is not None:
            if node.tag == "-text":
                time_text += node.text(strip=True)
            node = node.next
        time_text = time_text.strip()

        entry.date = parse_vlr_date(date_text)
        entry.time = parse_vlr_time(time_text)
        entry.datetime = parse_vlr_datetime(date_text, time_text, source_tz=source_tz)

    return entry


def _has_next_page(html: HTMLParser) -> bool:
    for link in html.css('link[rel="next"]'):
        return True
    return False


def parse_player_matches(html: HTMLParser, source_tz: ZoneInfo | tzinfo | None = None) -> MatchHistoryPage:
    page = MatchHistoryPage()
    for a in html.css("a.m-item"):
        page.matches.append(_parse_match_item(a, source_tz=source_tz))
    page.has_next_page = _has_next_page(html)
    return page
