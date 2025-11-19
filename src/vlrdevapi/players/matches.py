"""Player matches functionality."""

from __future__ import annotations

import datetime
from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import Match, MatchTeam
from ..config import get_config
from ..fetcher import batch_fetch_html
from ..utils import absolute_url, extract_text, normalize_whitespace

_config = get_config()


def matches(
    player_id: int,
    limit: int | None = None,
    page: int | None = None,
    timeout: float | None = None,
) -> list[Match]:
    """
    Get player match history with batch fetching for pagination.
    
    Args:
        player_id: Player ID
        limit: Maximum number of matches to return
        page: Page number (1-indexed)
        timeout: Request timeout in seconds
    
    Returns:
        List of player matches. Each match includes:
        - stage: The tournament stage (e.g., "Group Stage", "Playoffs")
        - phase: The specific phase within the stage (e.g., "W1", "GF")
    
    Example:
        >>> import vlrdevapi as vlr
        >>> matches = vlr.players.matches(player_id=123, limit=10)
        >>> for match in matches:
        ...     print(f"{match.event} - {match.stage} {match.phase}: {match.result}")
    """
    start_page = page or 1
    results: list[Match] = []
    
    remaining: int | None
    if limit is None:
        remaining = None
    else:
        remaining = max(0, min(1000, limit))
        if remaining == 0:
            return []
    
    single_page_only = limit is None and page is not None
    current_page = start_page
    pages_fetched = 0
    MAX_PAGES = 25
    BATCH_SIZE = 3  # Fetch 3 pages at a time
    
    while pages_fetched < MAX_PAGES:
        # Determine how many pages to fetch in this batch
        pages_to_fetch = min(BATCH_SIZE, MAX_PAGES - pages_fetched)
        if single_page_only:
            pages_to_fetch = 1
        
        # Build URLs for batch fetching
        urls: list[str] = []
        for i in range(pages_to_fetch):
            page_num = current_page + i
            suffix = f"?page={page_num}" if page_num > 1 else ""
            url = f"{_config.vlr_base}/player/matches/{player_id}{suffix}"
            urls.append(url)
        
        # Batch fetch all pages concurrently
        effective_timeout = timeout if timeout is not None else _config.default_timeout
        batch_results = batch_fetch_html(urls, timeout=effective_timeout, max_workers=min(3, len(urls)))
        
        # Process each page in order
        for url in urls:
            html = batch_results.get(url)
            
            if isinstance(html, Exception) or not html:
                # Stop if we hit an error
                pages_fetched = MAX_PAGES
                break
            
            soup = BeautifulSoup(html, "lxml")
            page_matches: list[Match] = []
            
            for anchor in soup.select("a.wf-card.fc-flex.m-item"):
                href_val = anchor.get("href")
                href = href_val if isinstance(href_val, str) else None
                if not href:
                    continue
                
                parts = href.strip("/").split("/")
                if not parts or not parts[0].isdigit():
                    continue
                match_id = int(parts[0])
                match_url = absolute_url(href) or ""
                
                # Parse event info
                event_el = anchor.select_one(".m-item-event")
                event_name = None
                stage = None
                phase = None
                if event_el:
                    strings = list(event_el.stripped_strings)
                    if strings:
                        event_name = normalize_whitespace(strings[0]) if strings[0] else None
                        details = [s.strip("⋅ ") for s in strings[1:] if s.strip("⋅ ")]
                        if details:
                            # Join all details and split on ⋅ separator
                            combined = " ".join(details)
                            if "⋅" in combined:
                                parts = [normalize_whitespace(p) for p in combined.split("⋅") if p.strip()]
                                if len(parts) >= 2:
                                    stage = parts[0]
                                    phase = parts[1]
                                elif len(parts) == 1:
                                    stage = parts[0]
                            else:
                                # No separator, treat as stage only
                                stage = normalize_whitespace(combined)
                
                # Parse teams
                team_blocks = anchor.select(".m-item-team")
                player_block = team_blocks[0] if team_blocks else None
                opponent_block = team_blocks[-1] if len(team_blocks) > 1 else None
                
                def parse_team_block(block: Tag | None) -> MatchTeam:
                    if not block:
                        return MatchTeam(name=None, tag=None, core=None)
                    name = extract_text(block.select_one(".m-item-team-name"))
                    tag = extract_text(block.select_one(".m-item-team-tag"))
                    core = extract_text(block.select_one(".m-item-team-core"))
                    return MatchTeam(name=name or None, tag=tag or None, core=core or None)
                
                player_team = parse_team_block(player_block)
                opponent_team = parse_team_block(opponent_block)
                
                # Parse result and scores
                result_el = anchor.select_one(".m-item-result")
                player_score: int | None = None
                opponent_score: int | None = None
                result = None
                
                if result_el:
                    spans: list[str] = [span.get_text(strip=True) for span in result_el.select("span")]
                    scores: list[int] = []
                    for value in spans:
                        try:
                                scores.append(int(value))
                        except ValueError:
                            continue
                    if len(scores) >= 2:
                        player_score, opponent_score = scores[0], scores[1]
                    elif len(scores) == 1:
                        player_score = scores[0]
                    
                    classes_val = result_el.get("class")
                    classes: list[str] = list(classes_val) if isinstance(classes_val, (list, tuple)) else []
                    if any("mod-win" == cls or cls.endswith("mod-win") for cls in classes):
                        result = "win"
                    elif any("mod-loss" == cls or cls.endswith("mod-loss") for cls in classes):
                        result = "loss"
                    elif any("mod-draw" == cls or cls.endswith("mod-draw") for cls in classes):
                        result = "draw"
                
                # Parse date/time
                date_el = anchor.select_one(".m-item-date")
                match_date = None
                match_time = None
                time_text = None
                
                if date_el:
                    parts_list = list(date_el.stripped_strings)
                    if parts_list:
                        date_text = parts_list[0]
                        try:
                            match_date = datetime.datetime.strptime(date_text, "%Y/%m/%d").date()
                        except ValueError:
                            pass
                        
                        if len(parts_list) > 1:
                            time_text = parts_list[1]
                            try:
                                match_time = datetime.datetime.strptime(time_text, "%I:%M %p").time()
                            except ValueError:
                                pass
                
                page_matches.append(Match(
                    match_id=match_id,
                    url=match_url,
                    event=event_name,
                    stage=stage,
                    phase=phase,
                    player_team=player_team,
                    opponent_team=opponent_team,
                    player_score=player_score,
                    opponent_score=opponent_score,
                    result=result,
                    date=match_date,
                    time=match_time,
                    time_text=time_text,
                ))
        
            if not page_matches:
                # No more matches on this page, stop fetching
                pages_fetched = MAX_PAGES
                break
            
            if remaining is None:
                results.extend(page_matches)
            else:
                take = page_matches[:remaining]
                results.extend(take)
                remaining -= len(take)
            
            pages_fetched += 1
            
            if single_page_only:
                pages_fetched = MAX_PAGES
                break
            if remaining is not None and remaining <= 0:
                pages_fetched = MAX_PAGES
                break
        
        current_page += pages_to_fetch
    
    return results
