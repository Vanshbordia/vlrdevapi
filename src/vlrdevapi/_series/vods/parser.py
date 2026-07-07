from selectolax.parser import HTMLParser

from vlrdevapi._series.vods.models import SeriesVod, SeriesVods


def parse_series_vods(html: HTMLParser) -> SeriesVods:
    """Parse VOD links from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        SeriesVods: Parsed VOD entries with URLs and labels.

    """
    result = SeriesVods()
    vods_container = html.css_first(".match-vods")
    if not vods_container:
        return result

    for a in vods_container.css("a"):
        href = a.attributes.get("href", "") or ""
        if not href:
            continue
        label = a.text(strip=True)
        if not label:
            continue
        result.vods.append(SeriesVod(url=href, label=label))

    return result
