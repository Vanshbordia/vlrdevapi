import contextlib
import re
from collections.abc import Callable
from typing import Protocol, TypeVar

from selectolax.lexbor import LexborHTMLParser as HTMLParser


def check_pagination(html: HTMLParser) -> bool:
    """Check whether a page after the current one exists.

    The active page is rendered as a ``mod-active`` span while other pages
    are anchor links. A terminal page still links back to earlier pages, so
    the mere presence of page links does not imply a next page. Compare the
    active page number against the highest page number offered instead.

    Args:
        html: Parsed HTML document.

    Returns:
        ``True`` if a page after the active one exists, ``False`` otherwise.

    """
    pagination_el = html.css_first("div.action-container-pages")
    if pagination_el is None:
        return False

    current_page = 1
    active = pagination_el.css_first(".btn.mod-page.mod-active")
    if active:
        with contextlib.suppress(ValueError):
            current_page = int(active.text(strip=True))

    max_page = current_page
    for btn in pagination_el.css(".btn.mod-page"):
        text = btn.text(strip=True)
        try:
            max_page = max(max_page, int(text))
        except ValueError:
            href = btn.attributes.get("href") or ""
            page_match = re.search(r"page=(\d+)", href)
            if page_match:
                max_page = max(max_page, int(page_match.group(1)))

    return current_page < max_page


class PageProtocol(Protocol):
    matches: list
    has_next_page: bool


PageT = TypeVar("PageT", bound=PageProtocol)


def collect_all_pages_sync(
    fetch_fn: Callable[[str], HTMLParser],
    build_url: Callable[[int], str],
    parse_fn: Callable[..., PageT],
    max_page: int,
    parse_extra: tuple = (),
) -> PageT:
    all_items = []
    current_page = 1
    while True:
        url = build_url(current_page)
        html = fetch_fn(url)
        page_data = parse_fn(html, *parse_extra)
        all_items.extend(page_data.matches)
        if not page_data.has_next_page or (max_page > 0 and current_page >= max_page):
            break
        current_page += 1
    page_data.matches = all_items
    page_data.has_next_page = False
    return page_data



