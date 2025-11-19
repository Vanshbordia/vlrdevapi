"""Event stages functionality."""

from __future__ import annotations

from urllib import parse
from bs4 import BeautifulSoup

from .models import EventStage
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text

_config = get_config()


def stages(event_id: int, timeout: float | None = None) -> list[EventStage]:
    """List available stages for an event's matches page.
    
    Returns a list of stage options with their series_id and URL. The special
    "All Stages" option will have series_id="all".
    """
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    soup = BeautifulSoup(html, "lxml")
    dropdown = soup.select_one("span.wf-dropdown.mod-all")
    if not dropdown:
        return []
    stages_list: list[EventStage] = []
    for a in dropdown.select("a"):
        name = (extract_text(a) or "").strip()
        href = a.get("href")
        if not href or not isinstance(href, str):
            continue
        full_url = parse.urljoin(f"{_config.vlr_base}/", href.lstrip("/"))
        # Parse series_id from query (?series_id=...)
        parsed = parse.urlparse(full_url)
        qs = parse.parse_qs(parsed.query)
        sid = (qs.get("series_id", ["all"]))[0] or "all"
        stages_list.append(EventStage(name=name, series_id=sid, url=full_url))
    return stages_list
