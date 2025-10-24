"""Player-related API endpoints and models."""

from __future__ import annotations

import datetime
import re
from bs4.element import Tag

from dataclasses import dataclass, field
from bs4 import BeautifulSoup

from .config import get_config
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

_config = get_config()

@dataclass(frozen=True)
class SocialLink:
    """Player social media link."""

    label: str
    url: str


@dataclass(frozen=True)
class Team:
    """Player team information."""

    role: str
    id: int | None = None
    name: str | None = None
    joined_date: datetime.date | None = None
    left_date: datetime.date | None = None


@dataclass(frozen=True)
class Profile:
    """Player profile information."""

    player_id: int
    handle: str | None = None
    real_name: str | None = None
    country: str | None = None
    avatar_url: str | None = None
    socials: list[SocialLink] = field(default_factory=list)
    current_teams: list[Team] = field(default_factory=list)
    past_teams: list[Team] = field(default_factory=list)


@dataclass(frozen=True)
class MatchTeam:
    """Team in a player match."""

    name: str | None = None
    tag: str | None = None
    core: str | None = None


@dataclass(frozen=True)
class Match:
    """Player match entry."""

    match_id: int
    url: str
    player_team: MatchTeam
    opponent_team: MatchTeam
    event: str | None = None
    stage: str | None = None
    phase: str | None = None
    player_score: int | None = None
    opponent_score: int | None = None
    result: str | None = None
    date: datetime.date | None = None
    time: datetime.time | None = None
    time_text: str | None = None


@dataclass(frozen=True)
class AgentStats:
    """Player agent statistics."""

    agent: str | None = None
    agent_image_url: str | None = None
    usage_count: int | None = None
    usage_percent: float | None = None
    rounds_played: int | None = None
    rating: float | None = None
    acs: float | None = None
    kd: float | None = None
    adr: float | None = None
    kast: float | None = None
    kpr: float | None = None
    apr: float | None = None
    fkpr: float | None = None
    fdpr: float | None = None
    kills: int | None = None
    deaths: int | None = None
    assists: int | None = None
    first_kills: int | None = None
    first_deaths: int | None = None


_MONTH_YEAR_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
    re.IGNORECASE,
)

_USAGE_RE = re.compile(r"\((\d+)\)\s*(\d+)%")


def _parse_month_year(text: str) -> datetime.date | None:
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


def _parse_usage(text: str | None) -> tuple[int | None, float | None]:
    """Parse usage text like '(10) 50%'."""
    if not text:
        return None, None
    match = _USAGE_RE.search(text)
    if match:
        count = parse_int(match.group(1))
        percent = parse_float(match.group(2))
        return count, percent / 100.0 if percent is not None else None
    return None, None


def profile(player_id: int, timeout: float | None = None) -> Profile | None:
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
    url = f"{_config.vlr_base}/player/{player_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".player-header")
    
    handle = extract_text(header.select_one("h1.wf-title")) if header else None
    real_name = extract_text(header.select_one(".player-real-name")) if header else None
    
    avatar_url = None
    if header:
        avatar_img = header.select_one(".wf-avatar img")
        if avatar_img:
            src_val = avatar_img.get("src")
            src = src_val if isinstance(src_val, str) else None
            if src:
                avatar_url = absolute_url(src)
    
    # Parse socials
    socials: list[SocialLink] = []
    if header:
        for anchor in header.select("a[href]"):
            href_val = anchor.get("href")
            href = href_val if isinstance(href_val, str) else None
            label = extract_text(anchor)
            if href and label:
                url_or = absolute_url(href) or href
                socials.append(SocialLink(label=label, url=url_or))
    
    # Parse country
    country = None
    if header:
        flag = header.select_one(".flag")
        if flag:
            classes_val = flag.get("class")
            classes: list[str] = list(classes_val) if isinstance(classes_val, (list, tuple)) else []
            for cls in classes:
                if cls.startswith("mod-") and cls != "mod-dark":
                    code: str = cls.removeprefix("mod-")
                    country = map_country_code(code)
                    break
    
    # Parse current teams
    current_teams: list[Team] = []
    label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        text = extract_text(h2) or ""
        if "current teams" in text.lower():
            label = h2
            break
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href_val = anchor.get("href")
                href = href_val.strip("/") if isinstance(href_val, str) else ""
                team_id = extract_id_from_url(href, "team") if href else None
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
    past_teams: list[Team] = []
    label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        text = extract_text(h2) or ""
        if "past teams" in text.lower():
            label = h2
            break
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href_val = anchor.get("href")
                href = href_val.strip("/") if isinstance(href_val, str) else ""
                team_id = extract_id_from_url(href, "team") if href else None
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
