from selectolax.parser import HTMLParser

from vlrdevapi._player.info.models import PlayerInfo
from vlrdevapi.commons.countries import get_country_name


def parse_player_info(html: HTMLParser) -> PlayerInfo:
    info = PlayerInfo()
    header = html.css_first(".player-header")
    if not header:
        return info

    name_el = header.css_first("h1.wf-title")
    if name_el:
        info.name = name_el.text(strip=True)

    real_el = header.css_first("h2.player-real-name")
    if real_el:
        info.real_name = real_el.text(strip=True)

    img_el = header.css_first(".wf-avatar.mod-player img")
    if img_el:
        src = img_el.attributes.get("src", "") or ""
        if src.startswith("//"):
            src = "https:" + src
        info.img = src

    for a in header.css("a[target='_blank']"):
        href = a.attributes.get("href", "") or ""
        text = a.text(strip=True)
        if href.startswith("https://x.com/"):
            info.x_link = href
            info.x_handle = text
        elif href.startswith("https://www.twitch.tv/"):
            info.twitch_link = href
            info.twitch_handle = text.removeprefix("twitch.tv/")

    flag_el = header.css_first("i.flag")
    if flag_el:
        for cls in (flag_el.attributes.get("class", "") or "").split():
            if cls.startswith("mod-"):
                info.country_code = cls[4:]
        if info.country_code:
            info.country = get_country_name(info.country_code)

    for span in header.css("span[style*='font-style: italic']"):
        raw = span.text(strip=True)
        if raw:
            info.aliases = [a.strip() for a in raw.split(",") if a.strip()]
            break

    return info
