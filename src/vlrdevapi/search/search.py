"""Search functionality for VLR.gg."""

from __future__ import annotations

import re
from typing import Optional, Literal, List
from urllib import parse

from bs4 import BeautifulSoup

from ..config import get_config

# Pre-compiled regex pattern for performance
_INACTIVE_RE = re.compile(r'\s*\(inactive\s*\)\s*', re.IGNORECASE)
from ..fetcher import fetch_html, batch_fetch_html
from ..exceptions import NetworkError
from ..utils import (
    extract_text,
    absolute_url,
    extract_id_from_url,
    normalize_whitespace,
)
from .. import players as players_api
from .. import teams as teams_api
from .models import (
    SearchPlayerResult,
    SearchTeamResult,
    SearchEventResult,
    SearchSeriesResult,
    SearchResults,
)

_config = get_config()

SearchType = Literal["all", "players", "teams", "events", "series"]


def _parse_search_results(
    soup: BeautifulSoup,
    query: str,
) -> SearchResults:
    """Parse search results from HTML."""
    players = []
    teams = []
    events = []
    series_results = []
    
    results_divs = soup.select("div.wf-card[style*='margin-top']")
    if not results_divs:
        return SearchResults(
            query=query,
            total_results=0,
            players=[],
            teams=[],
            events=[],
            series=[],
        )
    
    for results_div in results_divs:
        for item in results_div.select("a.wf-module-item.search-item"):
            href = item.get("href", "")
            if not href:
                continue
            
            full_url = absolute_url(href) or ""
            
            title_el = item.select_one(".search-item-title")
            title = normalize_whitespace(extract_text(title_el)) if title_el else None
            
            desc_el = item.select_one(".search-item-desc")
            desc_text = normalize_whitespace(extract_text(desc_el)) if desc_el else ""
            
            img_el = item.select_one("img")
            img_url = absolute_url(img_el.get("src")) if img_el and img_el.get("src") else None
            
            if "/player/" in href:
                player_id = extract_id_from_url(href, "player")
                if player_id:
                    real_name = None
                    if desc_el:
                        italic_span = desc_el.select_one("span[style*='italic']")
                        if italic_span:
                            real_name = normalize_whitespace(extract_text(italic_span))
                    
                    players.append(SearchPlayerResult(
                        player_id=player_id,
                        url=full_url,
                        ign=title,
                        real_name=real_name,
                        image_url=img_url,
                    ))
            
            elif "/team/" in href:
                team_id = extract_id_from_url(href, "team")
                if team_id:
                    is_inactive = "inactive" in desc_text.lower() or "inactive" in title.lower() if title else False
                    
                    clean_title = title
                    if clean_title and "inactive" in clean_title.lower():
                        clean_title = _INACTIVE_RE.sub('', clean_title).strip()
                    
                    teams.append(SearchTeamResult(
                        team_id=team_id,
                        url=full_url,
                        name=clean_title,
                        logo_url=img_url,
                        is_inactive=is_inactive,
                    ))
            
            elif "/event/" in href:
                event_id = extract_id_from_url(href, "event")
                if event_id:
                    date_range = None
                    prize = None
                    
                    if desc_text:
                        parts = desc_text.split("event")
                        if len(parts) > 1:
                            details = parts[1].strip()
                            detail_parts = [p.strip() for p in details.split("–") if p.strip()]
                            
                            if detail_parts:
                                date_part = detail_parts[0].strip()
                                if date_part and not date_part.startswith("$"):
                                    date_range = date_part
                                
                                for part in detail_parts:
                                    if "$" in part:
                                        prize = part.strip()
                                        break
                    
                    events.append(SearchEventResult(
                        event_id=event_id,
                        url=full_url,
                        name=title,
                        date_range=date_range,
                        prize=prize,
                        image_url=img_url,
                    ))
            
            elif "/series/" in href:
                series_id = extract_id_from_url(href, "series")
                if series_id:
                    series_results.append(SearchSeriesResult(
                        series_id=series_id,
                        url=full_url,
                        name=title,
                        image_url=img_url,
                    ))
    
    total = len(players) + len(teams) + len(events) + len(series_results)
    
    return SearchResults(
        query=query,
        total_results=total,
        players=players,
        teams=teams,
        events=events,
        series=series_results,
    )


def search(
    query: str,
    search_type: SearchType = "all",
    timeout: float | None = None,
) -> SearchResults:
    """
    Search VLR.gg for players, teams, events, and series.
    
    Args:
        query: Search query string
        search_type: Type of search - "all", "players", "teams", "events", or "series"
        timeout: Request timeout in seconds
    
    Returns:
        SearchResults object containing all matching results
    
    Raises:
        NetworkError: If the request fails
    
    Example:
        >>> import vlrdevapi as vlr
        >>> results = vlr.search.search("nrg")
        >>> print(f"Found {results.total_results} results")
        >>> for player in results.players:
        ...     print(f"Player: {player.ign}")
        >>> for team in results.teams:
        ...     print(f"Team: {team.name}")
    """
    if not query or not query.strip():
        return SearchResults(
            query=query,
            total_results=0,
            players=[],
            teams=[],
            events=[],
            series=[],
        )
    
    query = query.strip()
    
    type_param = search_type if search_type != "all" else "all"
    
    params = {
        "q": query,
        "type": type_param,
    }
    url = f"{_config.vlr_base}/search/?{parse.urlencode(params)}"
    
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    html = fetch_html(url, effective_timeout)
    soup = BeautifulSoup(html, "lxml")
    
    results = _parse_search_results(soup, query)
    
    # Enrich players with country (and names if missing) using batch fetching
    enriched_players: List[SearchPlayerResult] = []
    if results.players:
        # Batch fetch all player profiles concurrently
        player_urls = [f"{_config.vlr_base}/player/{p.player_id}" for p in results.players]
        player_htmls = batch_fetch_html(player_urls, timeout=effective_timeout, max_workers=min(4, len(player_urls)))
        
        for p, url in zip(results.players, player_urls):
            country = p.country
            ign = p.ign
            real_name = p.real_name
            
            html = player_htmls.get(url)
            if html and not isinstance(html, Exception):
                try:
                    soup = BeautifulSoup(html, "lxml")
                    header = soup.select_one(".player-header")
                    
                    if header:
                        # Extract handle
                        if not ign:
                            handle_el = header.select_one("h1.wf-title")
                            if handle_el:
                                ign = extract_text(handle_el)
                        
                        # Extract real name
                        if not real_name:
                            real_name_el = header.select_one(".player-real-name")
                            if real_name_el:
                                real_name = extract_text(real_name_el)
                        
                        # Extract country
                        if not country:
                            flag = header.select_one(".flag")
                            if flag:
                                for cls in flag.get("class", []):
                                    if cls.startswith("mod-") and cls != "mod-dark":
                                        from ..countries import map_country_code
                                        code = cls.removeprefix("mod-")
                                        country = map_country_code(code)
                                        break
                except Exception:
                    pass
            
            enriched_players.append(SearchPlayerResult(
                player_id=p.player_id,
                url=p.url,
                ign=ign,
                real_name=real_name,
                country=country,
                image_url=p.image_url,
            ))
    
    # Enrich teams with country and active flag using batch fetching
    enriched_teams: List[SearchTeamResult] = []
    if results.teams:
        # Batch fetch all team info pages concurrently
        team_urls = [f"{_config.vlr_base}/team/{t.team_id}" for t in results.teams]
        team_htmls = batch_fetch_html(team_urls, timeout=effective_timeout, max_workers=min(4, len(team_urls)))
        
        for t, url in zip(results.teams, team_urls):
            country = t.country
            is_inactive = t.is_inactive
            name = t.name
            
            html = team_htmls.get(url)
            if html and not isinstance(html, Exception):
                try:
                    soup = BeautifulSoup(html, "lxml")
                    header = soup.select_one(".team-header")
                    
                    if header:
                        # Extract team name
                        if not name:
                            name_el = header.select_one("h1.wf-title")
                            if name_el:
                                name = extract_text(name_el)
                        
                        # Check if team is active
                        status_el = header.select_one(".team-header-status")
                        if status_el:
                            status_text = extract_text(status_el).lower()
                            if "inactive" in status_text:
                                is_inactive = True
                            else:
                                is_inactive = False
                        
                        # Extract country
                        if not country:
                            country_el = header.select_one(".team-header-country")
                            if country_el:
                                flag = country_el.select_one(".flag")
                                if flag:
                                    for cls in flag.get("class", []):
                                        if cls.startswith("mod-") and cls != "mod-dark":
                                            from ..countries import map_country_code
                                            code = cls.removeprefix("mod-")
                                            country = map_country_code(code)
                                            break
                except Exception:
                    pass
            
            enriched_teams.append(SearchTeamResult(
                team_id=t.team_id,
                url=t.url,
                name=name,
                country=country,
                logo_url=t.logo_url,
                is_inactive=is_inactive,
            ))
    
    # Return new SearchResults with enriched data
    return SearchResults(
        query=results.query,
        total_results=results.total_results,
        players=enriched_players,
        teams=enriched_teams,
        events=results.events,
        series=results.series,
    )


def search_players(
    query: str,
    timeout: float | None = None,
) -> list[SearchPlayerResult]:
    """
    Search for players only.
    
    Args:
        query: Search query string
        timeout: Request timeout in seconds
    
    Returns:
        List of player search results
    
    Example:
        >>> import vlrdevapi as vlr
        >>> players = vlr.search.search_players("tenz")
        >>> for player in players:
        ...     print(f"{player.ign} - {player.real_name}")
    """
    results = search(query, search_type="players", timeout=timeout)
    return results.players


def search_teams(
    query: str,
    timeout: float | None = None,
) -> list[SearchTeamResult]:
    """
    Search for teams only.
    
    Args:
        query: Search query string
        timeout: Request timeout in seconds
    
    Returns:
        List of team search results
    
    Example:
        >>> import vlrdevapi as vlr
        >>> teams = vlr.search.search_teams("sentinels")
        >>> for team in teams:
        ...     print(f"{team.name} - Active: {not team.is_inactive}")
    """
    results = search(query, search_type="teams", timeout=timeout)
    return results.teams


def search_events(
    query: str,
    timeout: float | None = None,
) -> list[SearchEventResult]:
    """
    Search for events only.
    
    Args:
        query: Search query string
        timeout: Request timeout in seconds
    
    Returns:
        List of event search results
    
    Example:
        >>> import vlrdevapi as vlr
        >>> events = vlr.search.search_events("champions")
        >>> for event in events:
        ...     print(f"{event.name} - {event.date_range}")
    """
    results = search(query, search_type="events", timeout=timeout)
    return results.events


def search_series(
    query: str,
    timeout: float | None = None,
) -> list[SearchSeriesResult]:
    """
    Search for series only.
    
    Args:
        query: Search query string
        timeout: Request timeout in seconds
    
    Returns:
        List of series search results
    
    Example:
        >>> import vlrdevapi as vlr
        >>> series = vlr.search.search_series("vct")
        >>> for s in series:
        ...     print(f"{s.name}")
    """
    results = search(query, search_type="series", timeout=timeout)
    return results.series
