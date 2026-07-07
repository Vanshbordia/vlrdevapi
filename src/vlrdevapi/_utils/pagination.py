from collections.abc import Callable
from typing import Protocol, TypeVar

from selectolax.parser import HTMLParser


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



