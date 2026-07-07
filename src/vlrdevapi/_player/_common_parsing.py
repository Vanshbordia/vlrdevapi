"""Shared parsing utilities for player sub-packages."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from typing import TYPE_CHECKING

from selectolax.parser import Node

if TYPE_CHECKING:
    from vlrdevapi._player.agents.models import AgentStats
    from vlrdevapi._player.teams.models import PlayerTeam

_MONTH_MAP: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

_MONTH_YEAR_RE = re.compile(
    r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})",
    re.IGNORECASE,
)

_DASHES = "\u2013\u2014\u2212-"


def _parse_month_year(text: str) -> datetime | None:
    m = _MONTH_YEAR_RE.search(text)
    if not m:
        return None
    month = _MONTH_MAP[m.group(1).lower()]
    year = int(m.group(2))
    return datetime(year, month, 1, tzinfo=timezone.utc)


def _parse_team_dates(text: str) -> tuple[date | None, date | None]:
    text = text.strip()
    if not text:
        return None, None
    lower = text.lower()
    if lower.startswith("joined in "):
        return _parse_month_year(text), None
    if lower.startswith("left in "):
        return None, _parse_month_year(text)
    parts = re.split(f"[{_DASHES}]", text)
    if len(parts) == 2:
        return _parse_month_year(parts[0]), _parse_month_year(parts[1])
    return None, None


def _parse_inactive_date(text: str) -> date | None:
    lower = text.lower()
    if lower.startswith("inactive from "):
        return _parse_month_year(text)
    return None


def _next_sibling_card(node: Node) -> Node | None:
    sibling = node.next
    while sibling is not None:
        if hasattr(sibling, "attributes"):
            classes = sibling.attributes.get("class", "") or ""
            if "wf-card" in classes:
                return sibling
        sibling = sibling.next
    return None


def _parse_team_entry(a: Node) -> PlayerTeam:
    from vlrdevapi._player.teams.models import PlayerTeam

    team = PlayerTeam(team_id=0, name="", slug="")
    href = a.attributes.get("href", "") or ""
    match = re.match(r"/team/(\d+)/([^/?#]+)", href)
    if match:
        team.team_id = int(match.group(1))
        team.slug = match.group(2)
    name_el = a.css_first('div[style*="font-weight: 500"]')
    if name_el:
        team.name = name_el.text(strip=True)
    img_el = a.css_first("img")
    if img_el:
        src = img_el.attributes.get("src", "") or ""
        if src.startswith("//"):
            src = "https:" + src
        team.logo_url = src
    light_divs = a.css("div.ge-text-light")
    joined: date | None = None
    left: date | None = None
    inactive: date | None = None
    for div in light_divs:
        style = div.attributes.get("style", "") or ""
        raw = div.text(strip=True)
        if not raw:
            continue
        if "font-style: italic" in style or "font-style:italic" in style:
            inactive = _parse_inactive_date(raw)
        else:
            jn, lt = _parse_team_dates(raw)
            if jn is not None or lt is not None:
                joined, left = jn, lt
    team.joined_date = joined
    team.left_date = left
    team.inactive_date = inactive
    return team


def _parse_float(text: str) -> float | None:
    cleaned = text.strip().replace("%", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_int(text: str) -> int | None:
    cleaned = text.strip()
    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_agent_row(tr: Node) -> AgentStats:
    from vlrdevapi._player.agents.models import AgentStats

    stats = AgentStats()
    tds = tr.css("td")

    if len(tds) < 17:
        return stats

    img_el = tds[0].css_first("img")
    if img_el:
        stats.agent = (img_el.attributes.get("alt", "") or "").title()

    use_span = tds[1].css_first("span")
    if use_span:
        stats.use = use_span.text(strip=True)
    else:
        stats.use = tds[1].text(strip=True)

    stats.rounds = _parse_int(tds[2].text(strip=True))
    stats.rating = _parse_float(tds[3].text(strip=True))
    stats.acs = _parse_float(tds[4].text(strip=True))
    stats.kd = _parse_float(tds[5].text(strip=True))
    stats.adr = _parse_float(tds[6].text(strip=True))
    stats.kast = tds[7].text(strip=True)
    stats.kpr = _parse_float(tds[8].text(strip=True))
    stats.apr = _parse_float(tds[9].text(strip=True))
    stats.fkpr = _parse_float(tds[10].text(strip=True))
    stats.fdpr = _parse_float(tds[11].text(strip=True))
    stats.kills = _parse_int(tds[12].text(strip=True))
    stats.deaths = _parse_int(tds[13].text(strip=True))
    stats.assists = _parse_int(tds[14].text(strip=True))
    stats.first_kills = _parse_int(tds[15].text(strip=True))
    stats.first_deaths = _parse_int(tds[16].text(strip=True))

    return stats
