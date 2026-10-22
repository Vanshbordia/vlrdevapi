import re

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._series.vods.models import SeriesStream, SeriesVod, SeriesVods


def parse_series_vods(html: HTMLParser) -> SeriesVods:
    """Parse streams and VOD links from the series page HTML.

    Supports both the newer ``.sm-vods`` "watch" module and the legacy
    ``.match-vods`` container. Live broadcasts and watch parties live in
    the separate ``.match-streams-container`` module.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        SeriesVods: Parsed streams and VOD entries.

    """
    result = SeriesVods()
    result.streams = _parse_streams(html)
    result.vods = _parse_vods(html)
    return result


def _parse_streams(html: HTMLParser) -> list[SeriesStream]:
    container = html.css_first(".match-streams-container.js-sm-grid")
    if not container:
        return []

    streams: list[SeriesStream] = []
    for item in container.css(".sm-btn"):
        link = item.css_first("a.sm-ext") or item.css_first("a.sm-body")
        if not link:
            continue
        href = link.attributes.get("href", "") or ""
        if not href:
            continue

        site = (item.attributes.get("data-site", "") or "").strip().lower()
        platform_el = item.css_first(".sm-ptext")
        if platform_el:
            platform = platform_el.text(strip=True).lower()
        else:
            platform = site

        name_el = item.css_first(".sm-name")
        channel = name_el.text(strip=True) if name_el else ""

        country_code = ""
        flag_el = item.css_first(".flag")
        if flag_el:
            for cls in (flag_el.attributes.get("class", "") or "").split():
                if cls.startswith("mod-"):
                    country_code = cls[4:]
                    break

        streams.append(
            SeriesStream(
                platform=platform,
                channel=channel,
                url=href,
                stream_type=(item.attributes.get("data-type", "") or "broadcast"),
                country_code=country_code,
            ),
        )

    return streams


def _parse_vods(html: HTMLParser) -> list[SeriesVod]:
    container = html.css_first(".sm-vods") or html.css_first(".match-vods")
    if not container:
        return []

    vods: list[SeriesVod] = []
    sm_vods = container.css(".sm-vod")
    if sm_vods:
        for vod in sm_vods:
            link = vod.css_first("a.sm-ext")
            if not link:
                continue
            href = link.attributes.get("href", "") or ""
            if not href:
                continue
            name_el = vod.css_first(".sm-vod-name")
            label = name_el.text(strip=True) if name_el else ""
            if not label:
                label = link.text(strip=True)
            vods.append(
                SeriesVod(
                    url=href,
                    label=label,
                    platform=(vod.attributes.get("data-site", "") or ""),
                    map_number=_parse_int(vod.css_first(".sm-vod-num")),
                    start_seconds=_parse_int(
                        vod.css_first("[data-embed-start]"),
                        attribute="data-embed-start",
                    ),
                ),
            )
        return vods

    for a in container.css("a"):
        href = a.attributes.get("href", "") or ""
        if not href:
            continue
        label = a.text(strip=True)
        if not label:
            continue
        vods.append(SeriesVod(url=href, label=label))

    return vods


def _parse_int(
    node: Node | None,
    *,
    attribute: str | None = None,
) -> int | None:
    if node is None:
        return None
    if attribute is not None:
        text = node.attributes.get(attribute, "") or ""
    else:
        text = node.text(strip=True)
    if not text:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    return int(match.group())
