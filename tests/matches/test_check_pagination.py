from selectolax.parser import HTMLParser

from vlrdevapi._matches.common import check_pagination


def _page(active: int, last: int) -> HTMLParser:
    btns = []
    for p in range(1, last + 1):
        if p == active:
            btns.append(f'<span class="btn mod-page mod-active">{p}</span>')
        else:
            btns.append(f'<a href="/matches/?page={p}" class="btn mod-page">{p}</a>')
    return HTMLParser(f'<div class="action-container-pages">{"".join(btns)}</div>')


def test_middle_page_has_next():
    assert check_pagination(_page(active=2, last=5)) is True


def test_terminal_page_no_next():
    # Last page still links back to earlier pages; must not report a next page.
    assert check_pagination(_page(active=5, last=5)) is False


def test_single_page_no_next():
    assert check_pagination(_page(active=1, last=1)) is False


def test_no_pagination_element():
    assert check_pagination(HTMLParser("<div></div>")) is False
