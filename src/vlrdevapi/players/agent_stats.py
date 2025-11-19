"""Player agent statistics functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .models import AgentStats
from ._parser import _parse_usage
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import (
    absolute_url,
    extract_text,
    parse_int,
    parse_float,
    parse_percent,
    normalize_whitespace,
)

_config = get_config()


def agent_stats(
    player_id: int,
    timespan: str = "all",
    timeout: float | None = None
) -> list[AgentStats]:
    """
    Get player agent statistics.
    
    Args:
        player_id: Player ID
        timespan: Timespan filter (e.g., "all", "60d", "90d")
        timeout: Request timeout in seconds
    
    Returns:
        List of agent statistics
    
    Example:
        >>> import vlrdevapi as vlr
        >>> stats = vlr.players.agent_stats(player_id=123)
        >>> for stat in stats:
        ...     print(f"{stat.agent}: {stat.rating} rating, {stat.acs} ACS")
    """
    timespan = timespan or "all"
    url = f"{_config.vlr_base}/player/{player_id}/?timespan={timespan}"
    
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("div.wf-card.mod-table table.wf-table")
    if not table:
        return []
    
    rows = table.select("tbody tr")
    stats: list[AgentStats] = []
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 17:
            continue
        
        agent_img = cells[0].select_one("img") if cells[0] else None
        agent_name_val = agent_img.get("alt") if agent_img else None
        agent_name = agent_name_val if isinstance(agent_name_val, str) else None
        src_val = agent_img.get("src") if agent_img else None
        src = src_val if isinstance(src_val, str) else None
        agent_img_url = absolute_url(src) if src else None
        
        usage_text = normalize_whitespace(extract_text(cells[1]))
        usage_count, usage_percent = _parse_usage(usage_text)
        
        rounds_played = parse_int(extract_text(cells[2]))
        rating = parse_float(extract_text(cells[3]))
        acs = parse_float(extract_text(cells[4]))
        kd = parse_float(extract_text(cells[5]))
        adr = parse_float(extract_text(cells[6]))
        kast = parse_percent(extract_text(cells[7]))
        kpr = parse_float(extract_text(cells[8]))
        apr = parse_float(extract_text(cells[9]))
        fkpr = parse_float(extract_text(cells[10]))
        fdpr = parse_float(extract_text(cells[11]))
        kills = parse_int(extract_text(cells[12]))
        deaths = parse_int(extract_text(cells[13]))
        assists = parse_int(extract_text(cells[14]))
        first_kills = parse_int(extract_text(cells[15]))
        first_deaths = parse_int(extract_text(cells[16]))
        
        stats.append(AgentStats(
            agent=normalize_whitespace(agent_name) if isinstance(agent_name, str) else None,
            agent_image_url=agent_img_url,
            usage_count=usage_count,
            usage_percent=usage_percent,
            rounds_played=rounds_played,
            rating=rating,
            acs=acs,
            kd=kd,
            adr=adr,
            kast=kast,
            kpr=kpr,
            apr=apr,
            fkpr=fkpr,
            fdpr=fdpr,
            kills=kills,
            deaths=deaths,
            assists=assists,
            first_kills=first_kills,
            first_deaths=first_deaths,
        ))
    
    return stats
