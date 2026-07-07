from selectolax.parser import HTMLParser

from vlrdevapi._player._common_parsing import (
    _next_sibling_card,
    _parse_agent_row,
    _parse_team_entry,
)
from vlrdevapi._player.profile.models import PlayerProfile
from vlrdevapi.commons.countries import get_country_name


def _parse_info(html: HTMLParser, profile: PlayerProfile) -> None:
    header = html.css_first(".player-header")
    if not header:
        return
    name_el = header.css_first("h1.wf-title")
    if name_el:
        profile.name = name_el.text(strip=True)
    real_el = header.css_first("h2.player-real-name")
    if real_el:
        profile.real_name = real_el.text(strip=True)
    img_el = header.css_first(".wf-avatar.mod-player img")
    if img_el:
        src = img_el.attributes.get("src", "") or ""
        if src.startswith("//"):
            src = "https:" + src
        profile.img = src
    for a in header.css("a[target='_blank']"):
        href = a.attributes.get("href", "") or ""
        text = a.text(strip=True)
        if href.startswith("https://x.com/"):
            profile.x_link = href
            profile.x_handle = text
        elif href.startswith("https://www.twitch.tv/"):
            profile.twitch_link = href
            profile.twitch_handle = text.removeprefix("twitch.tv/")
    flag_el = header.css_first("i.flag")
    if flag_el:
        for cls in (flag_el.attributes.get("class", "") or "").split():
            if cls.startswith("mod-"):
                profile.country_code = cls[4:]
        if profile.country_code:
            profile.country = get_country_name(profile.country_code)
    for span in header.css("span[style*='font-style: italic']"):
        raw = span.text(strip=True)
        if raw:
            profile.aliases = [a.strip() for a in raw.split(",") if a.strip()]
            break


def _parse_current_team(html: HTMLParser, profile: PlayerProfile) -> None:
    labels = html.css("h2.wf-label.mod-large")
    for label in labels:
        text = label.text(strip=True)
        if text == "Current Teams":
            card = _next_sibling_card(label)
            if card is None:
                continue
            entries = card.css("a.wf-module-item")
            if entries:
                profile.current_team = _parse_team_entry(entries[0])
            break


def _parse_agents(html: HTMLParser, profile: PlayerProfile) -> None:
    for label in html.css("div.wf-label.mod-large"):
        if label.text(strip=True) == "Agents":
            search_from = label.parent or label
            card = _next_sibling_card(search_from)
            if card is None:
                break
            table = card.css_first("table.wf-table")
            if table is None:
                break
            tbody = table.css_first("tbody")
            if tbody is None:
                break
            for tr in tbody.css("tr"):
                profile.top_agents.append(_parse_agent_row(tr))
            break


def parse_player_profile(html: HTMLParser, timespan: str = "30d") -> PlayerProfile:
    profile = PlayerProfile()
    profile.stats_timespan = timespan
    _parse_info(html, profile)
    _parse_current_team(html, profile)
    _parse_agents(html, profile)
    return profile
