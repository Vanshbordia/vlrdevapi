from selectolax.parser import HTMLParser

from vlrdevapi._player._common_parsing import (
    _next_sibling_card,
    _parse_agent_row,
)
from vlrdevapi._player.agents.models import AgentStatsPage


def parse_agent_stats(html: HTMLParser, timespan: str = "all") -> AgentStatsPage:
    page = AgentStatsPage(timespan=timespan)

    for label in html.css("div.wf-label.mod-large"):
        if label.text(strip=True) == "Agents":
            search_from = label.parent or label
            card = _next_sibling_card(search_from)
            if card is None:
                break
            table = card.css_first("table.wf-table")
            if table is None:
                break
            tbody = table.css_first("tbody")
            if tbody is None:
                break
            for tr in tbody.css("tr"):
                page.agents.append(_parse_agent_row(tr))
            break

    return page
