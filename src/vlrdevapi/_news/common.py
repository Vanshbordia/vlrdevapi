from selectolax.parser import HTMLParser


def get_page_number(html: HTMLParser) -> int:
    """Get the current page number from the pagination controls.

    Args:
        html: Parsed HTML document.

    Returns:
        The active page number, or ``1`` if no pagination is present.

    """
    active_el = html.css_first("div.action-container-pages .btn.mod-page.mod-active")
    
    if active_el is None:
        return 1
    
    try:
        return int(active_el.text(strip=True))
    except ValueError:
        return 1


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