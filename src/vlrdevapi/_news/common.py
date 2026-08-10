from html.parser import HTMLParser
from datetime import date, datetime, tzinfo


def check_pagination(html: HTMLParser) -> bool:
    """Check whether the page has pagination links to additional pages.

    Args:
        html: Parsed HTML document.

    Returns:
        ``True`` if at least one page link exists, ``False`` otherwise.

    """
    pagination_el = html.css_first("div.action-container-pages")
    if pagination_el:
        page_links = pagination_el.css("a.btn.mod-page")
        return len(page_links) > 0
    return False