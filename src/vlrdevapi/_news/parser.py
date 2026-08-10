"""Parse news from the vlr.gg/news HTML page."""

import logging
from datetime import datetime

from selectolax.parser import HTMLParser, Node

from vlrdevapi._news.common import check_pagination, get_page_number
from vlrdevapi._news.models import News, NewsPage
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.commons.datetime import date_to_utc_datetime

logger = logging.getLogger(__name__)


def parse_news_page(html: HTMLParser) -> NewsPage:
    """Parse the vlr.gg/news page and extract news entries.

    Args:
        html: Parsed HTML document.

    Returns:
        NewsPage: Container with a list of ``News`` entries and a
            ``has_next_page`` flag.

    """
    news = []
    
    for item in html.css("a.wf-module-item"):
        parsed = _parse_news_item(item)
    
        if parsed is not None:
            news.append(parsed)

    has_next_page = check_pagination(html)
    page_number = get_page_number(html)
    return NewsPage(news=news, has_next_page=has_next_page, page_number=page_number)


def _parse_news_item(item: Node) -> News | None:
    """Parse a single news entry from a ``a.wf-module-item`` anchor.

    Args:
        item: The ``a.wf-module-item`` DOM node.

    Returns:
        A ``News`` entry, or ``None`` if parsing fails.

    """
    try:
        news = News()

        href = item.attributes.get("href") or ""
        news.link = href
        
        if href.startswith("/"):
            news.id = int(href.strip("/").split("/")[0])

        text_divs = item.css("div > div:not(.ge-text-light)")

        if text_divs:
            news.title = text_divs[0].text(strip=True)
        if len(text_divs) > 1:
            news.subtitle = text_divs[1].text(strip=True)

        flag_el = item.css_first("i.flag")
        
        if flag_el:
            for cls in (flag_el.attributes.get("class") or "").split():
                if cls.startswith("mod-"):
                    news.country_name = get_country_name(cls[4:])
                    break

        meta_el = item.css_first("div.ge-text-light")
        
        if meta_el:
            for child in meta_el.iter(include_text=True):
                if child.tag != "-text":
                    continue
                part = child.text(strip=True)
                if not part:
                    continue
                
                if part.startswith("by "):
                    news.author = part.removeprefix("by ").strip()
                else:
                    try:
                        parsed_date = datetime.strptime(part, "%B %d, %Y").date()
                    except ValueError:
                        pass
                    else:
                        news.date = date_to_utc_datetime(parsed_date)

    except (AttributeError, IndexError, ValueError):
        logger.debug("Failed to parse news item", exc_info=True)
        return None
    else:
        return news
