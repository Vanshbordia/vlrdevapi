from selectolax.parser import HTMLParser

from vlrdevapi._series.vods.models import SeriesVod, SeriesVods


def parse_series_vods(html: HTMLParser) -> SeriesVods:
    """Parse VOD links from the series page HTML.

    Supports both the newer ``.sm-vods`` "watch" module and the legacy
    ``.match-vods`` container.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        SeriesVods: Parsed VOD entries with URLs and labels.

    """
    result = SeriesVods()

    container = html.css_first(".sm-vods") or html.css_first(".match-vods")
    if not container:
        return result

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
            result.vods.append(SeriesVod(url=href, label=label))
        return result

    for a in container.css("a"):
        href = a.attributes.get("href", "") or ""
        if not href:
            continue
        label = a.text(strip=True)
        if not label:
            continue
        result.vods.append(SeriesVod(url=href, label=label))

    return result
