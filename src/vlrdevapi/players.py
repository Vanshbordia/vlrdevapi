"""Player-related API endpoints and models."""

from __future__ import annotations

import datetime
import re
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict
from bs4 import BeautifulSoup

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .countries import map_country_code
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import (
    extract_text,
    absolute_url,
    extract_id_from_url,
    parse_int,
    parse_float,
    parse_percent,
    normalize_whitespace,
)

class SocialLink(BaseModel):
    """Player social media link."""
    
    model_config = ConfigDict(frozen=True)
    
    label: str = Field(description="Link label")
    url: str = Field(description="Link URL")


class Team(BaseModel):
    """Player team information."""
    
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = Field(None, description="Team ID")
    name: Optional[str] = Field(None, description="Team name")
    role: str = Field(description="Player role")
    joined_date: Optional[datetime.date] = Field(None, description="Join date")
    left_date: Optional[datetime.date] = Field(None, description="Leave date")


class Profile(BaseModel):
    """Player profile information."""
    
    model_config = ConfigDict(frozen=True)
    
    player_id: int = Field(description="Player ID")
    handle: Optional[str] = Field(None, description="Player handle/IGN")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Country")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    socials: List[SocialLink] = Field(default_factory=list, description="Social links")
    current_teams: List[Team] = Field(default_factory=list, description="Current teams")
    past_teams: List[Team] = Field(default_factory=list, description="Past teams")


class MatchTeam(BaseModel):
    """Team in a player match."""
    
    model_config = ConfigDict(frozen=True)
    
    name: Optional[str] = Field(None, description="Team name")
    tag: Optional[str] = Field(None, description="Team tag")
    core: Optional[str] = Field(None, description="Core roster")


class Match(BaseModel):
    """Player match entry."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: int = Field(description="Match ID")
    url: str = Field(description="Match URL")
    event: Optional[str] = Field(None, description="Event name")
    stage: Optional[str] = Field(None, description="Stage name (e.g., 'Group Stage')")
    phase: Optional[str] = Field(None, description="Phase name (e.g., 'W1')")
    player_team: MatchTeam = Field(description="Player's team")
    opponent_team: MatchTeam = Field(description="Opponent team")
    player_score: Optional[int] = Field(None, description="Player team score")
    opponent_score: Optional[int] = Field(None, description="Opponent score")
    result: Optional[str] = Field(None, description="Match result (win/loss/draw)")
    date: Optional[datetime.date] = Field(None, description="Match date")
    time: Optional[datetime.time] = Field(None, description="Match time")
    time_text: Optional[str] = Field(None, description="Time text")


class AgentStats(BaseModel):
    """Player agent statistics."""
    
    model_config = ConfigDict(frozen=True)
    
    agent: Optional[str] = Field(None, description="Agent name")
    agent_image_url: Optional[str] = Field(None, description="Agent image URL")
    usage_count: Optional[int] = Field(None, description="Times played")
    usage_percent: Optional[float] = Field(None, description="Usage percentage")
    rounds_played: Optional[int] = Field(None, description="Rounds played")
    rating: Optional[float] = Field(None, description="Rating")
    acs: Optional[float] = Field(None, description="Average combat score")
    kd: Optional[float] = Field(None, description="K/D ratio")
    adr: Optional[float] = Field(None, description="Average damage per round")
    kast: Optional[float] = Field(None, description="KAST percentage")
    kpr: Optional[float] = Field(None, description="Kills per round")
    apr: Optional[float] = Field(None, description="Assists per round")
    fkpr: Optional[float] = Field(None, description="First kills per round")
    fdpr: Optional[float] = Field(None, description="First deaths per round")
    kills: Optional[int] = Field(None, description="Total kills")
    deaths: Optional[int] = Field(None, description="Total deaths")
    assists: Optional[int] = Field(None, description="Total assists")
    first_kills: Optional[int] = Field(None, description="Total first kills")
    first_deaths: Optional[int] = Field(None, description="Total first deaths")


_MONTH_YEAR_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
    re.IGNORECASE,
)

_USAGE_RE = re.compile(r"\((\d+)\)\s*(\d+)%")


def _parse_month_year(text: str) -> Optional[datetime.date]:
    """Parse month-year format to date."""
    match = _MONTH_YEAR_RE.search(text)
    if not match:
        return None
    month_name, year_str = match.groups()
    try:
        month = datetime.datetime.strptime(month_name.title(), "%B").month
        return datetime.date(int(year_str), month, 1)
    except ValueError:
        return None


def _parse_usage(text: Optional[str]) -> Tuple[Optional[int], Optional[float]]:
    """Parse usage text like '(10) 50%'."""
    if not text:
        return None, None
    match = _USAGE_RE.search(text)
    if match:
        count = parse_int(match.group(1))
        percent = parse_float(match.group(2))
        return count, percent / 100.0 if percent is not None else None
    return None, None


def profile(player_id: int, timeout: float = DEFAULT_TIMEOUT) -> Optional[Profile]:
    """
    Get player profile information.
    
    Args:
        player_id: Player ID
        timeout: Request timeout in seconds
    
    Returns:
        Player profile or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> profile = vlr.players.profile(player_id=123)
        >>> print(f"{profile.handle} from {profile.country}")
    """
    url = f"{VLR_BASE}/player/{player_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".player-header")
    
    handle = extract_text(header.select_one("h1.wf-title")) if header else None
    real_name = extract_text(header.select_one(".player-real-name")) if header else None
    
    avatar_url = None
    if header:
        avatar_img = header.select_one(".wf-avatar img")
        if avatar_img and avatar_img.get("src"):
            avatar_url = absolute_url(avatar_img.get("src"))
    
    # Parse socials
    socials: List[SocialLink] = []
    if header:
        for anchor in header.select("a[href]"):
            href = anchor.get("href")
            label = extract_text(anchor)
            if href and label:
                socials.append(SocialLink(label=label, url=absolute_url(href) or href))
    
    # Parse country
    country = None
    if header:
        flag = header.select_one(".flag")
        if flag:
            for cls in flag.get("class", []):
                if cls.startswith("mod-") and cls != "mod-dark":
                    code = cls.removeprefix("mod-")
                    country = map_country_code(code)
                    break
    
    # Parse current teams
    current_teams: List[Team] = []
    label = soup.find("h2", class_="wf-label mod-large", string=lambda t: t and "Current Teams" in t)
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href = anchor.get("href", "").strip("/")
                team_id = extract_id_from_url(href, "team")
                name_el = anchor.select_one("div[style][style*='font-weight']") or anchor
                team_name = extract_text(name_el).strip() if name_el else None
                
                role_el = anchor.select_one("span.wf-tag")
                role = extract_text(role_el).strip().title() if role_el else "Player"
                
                joined_date = None
                for meta in anchor.select(".ge-text-light"):
                    text = extract_text(meta)
                    if "joined" in text.lower():
                        joined_date = _parse_month_year(text)
                        break
                
                current_teams.append(Team(
                    id=team_id,
                    name=team_name,
                    role=role,
                    joined_date=joined_date,
                    left_date=None,
                ))
    
    # Parse past teams
    past_teams: List[Team] = []
    label = soup.find("h2", class_="wf-label mod-large", string=lambda t: t and "Past Teams" in t)
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href = anchor.get("href", "").strip("/")
                team_id = extract_id_from_url(href, "team")
                name_el = anchor.select_one("div[style][style*='font-weight']") or anchor
                team_name = extract_text(name_el).strip() if name_el else None
                
                role_el = anchor.select_one("span.wf-tag")
                role = extract_text(role_el).strip().title() if role_el else "Player"
                
                joined_date = None
                left_date = None
                for meta in anchor.select(".ge-text-light"):
                    text = extract_text(meta)
                    if "-" in text or "–" in text:
                        normalized = text.replace("\u2013", "-").replace("–", "-")
                        parts = [part.strip() for part in normalized.split("-") if part.strip()]
                        if parts:
                            joined_date = _parse_month_year(parts[0])
                            if len(parts) > 1 and "present" not in parts[1].lower():
                                left_date = _parse_month_year(parts[1])
                        break
                
                past_teams.append(Team(
                    id=team_id,
                    name=team_name,
                    role=role,
                    joined_date=joined_date,
                    left_date=left_date,
                ))
    
    return Profile(
        player_id=player_id,
        handle=handle,
        real_name=real_name,
        country=country,
        avatar_url=avatar_url,
        socials=socials,
        current_teams=current_teams,
        past_teams=past_teams,
    )


def matches(
    player_id: int,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[Match]:
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
    results: List[Match] = []
    
    remaining: Optional[int]
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
        urls = []
        for i in range(pages_to_fetch):
            page_num = current_page + i
            suffix = f"?page={page_num}" if page_num > 1 else ""
            url = f"{VLR_BASE}/player/matches/{player_id}{suffix}"
            urls.append(url)
        
        # Batch fetch all pages concurrently
        batch_results = batch_fetch_html(urls, timeout=timeout, max_workers=min(3, len(urls)))
        
        # Process each page in order
        for page_idx, url in enumerate(urls):
            html = batch_results.get(url)
            
            if isinstance(html, Exception) or not html:
                # Stop if we hit an error
                pages_fetched = MAX_PAGES
                break
            
            soup = BeautifulSoup(html, "lxml")
            page_matches: List[Match] = []
            
            for anchor in soup.select("a.wf-card.fc-flex.m-item"):
                href = anchor.get("href")
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
                
                def parse_team_block(block):
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
                player_score = None
                opponent_score = None
                result = None
                
                if result_el:
                    spans = [span.get_text(strip=True) for span in result_el.select("span")]
                    scores = []
                    for value in spans:
                        try:
                            scores.append(int(value))
                        except ValueError:
                            continue
                    if len(scores) >= 2:
                        player_score, opponent_score = scores[0], scores[1]
                    elif len(scores) == 1:
                        player_score = scores[0]
                    
                    classes = result_el.get("class", [])
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
                    parts = list(date_el.stripped_strings)
                    if parts:
                        date_text = parts[0]
                        try:
                            match_date = datetime.datetime.strptime(date_text, "%Y/%m/%d").date()
                        except ValueError:
                            pass
                        
                        if len(parts) > 1:
                            time_text = parts[1]
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


def agent_stats(
    player_id: int,
    timespan: str = "all",
    timeout: float = DEFAULT_TIMEOUT
) -> List[AgentStats]:
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
    url = f"{VLR_BASE}/player/{player_id}/?timespan={timespan}"
    
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("div.wf-card.mod-table table.wf-table")
    if not table:
        return []
    
    rows = table.select("tbody tr")
    stats: List[AgentStats] = []
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 17:
            continue
        
        agent_img = cells[0].select_one("img") if cells[0] else None
        agent_name = agent_img.get("alt") if agent_img else None
        agent_img_url = absolute_url(agent_img.get("src")) if agent_img and agent_img.get("src") else None
        
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
            agent=normalize_whitespace(agent_name) if agent_name else None,
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
