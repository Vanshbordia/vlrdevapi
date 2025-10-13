"""Series/match-related API endpoints and models."""

from __future__ import annotations

import datetime
import re
from typing import List, Optional, Tuple, Dict
from urllib import request

from pydantic import BaseModel, Field, ConfigDict
from bs4 import BeautifulSoup

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .countries import COUNTRY_MAP
from .fetcher import fetch_html
from .exceptions import NetworkError
from .utils import extract_text, parse_int, parse_float, extract_id_from_url

class TeamInfo(BaseModel):
    """Team information in a series."""
    
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = Field(None, description="Team ID")
    name: str = Field(description="Team name")
    short: Optional[str] = Field(None, description="Team short tag")
    country: Optional[str] = Field(None, description="Team country")
    country_code: Optional[str] = Field(None, description="Country code")
    score: Optional[int] = Field(None, description="Team score")


class MapAction(BaseModel):
    """Map pick/ban action."""
    
    model_config = ConfigDict(frozen=True)
    
    action: str = Field(description="Action type (pick/ban)")
    team: str = Field(description="Team name")
    map: str = Field(description="Map name")


class Info(BaseModel):
    """Series information."""
    
    model_config = ConfigDict(frozen=True)
    
    match_id: int = Field(description="Match ID")
    teams: Tuple[TeamInfo, TeamInfo] = Field(description="Teams")
    score: Tuple[Optional[int], Optional[int]] = Field(description="Match score")
    status_note: str = Field(description="Status note")
    best_of: Optional[str] = Field(None, description="Best of format")
    event: str = Field(description="Event name")
    event_phase: str = Field(description="Event phase")
    date: Optional[datetime.date] = Field(None, description="Match date")
    time: Optional[datetime.time] = Field(None, description="Match time")
    map_actions: List[MapAction] = Field(default_factory=list, description="All map actions")
    picks: List[MapAction] = Field(default_factory=list, description="Map picks")
    bans: List[MapAction] = Field(default_factory=list, description="Map bans")
    remaining: Optional[str] = Field(None, description="Remaining map")


class PlayerStats(BaseModel):
    """Player statistics in a map."""
    
    model_config = ConfigDict(frozen=True)
    
    country: Optional[str] = Field(None, description="Player country")
    name: str = Field(description="Player name")
    team_short: Optional[str] = Field(None, description="Team short tag")
    team_id: Optional[int] = Field(None, description="Team ID")
    player_id: Optional[int] = Field(None, description="Player ID")
    agents: List[str] = Field(default_factory=list, description="Agents played")
    r: Optional[float] = Field(None, description="Rating")
    acs: Optional[int] = Field(None, description="Average combat score")
    k: Optional[int] = Field(None, description="Kills")
    d: Optional[int] = Field(None, description="Deaths")
    a: Optional[int] = Field(None, description="Assists")
    kd_diff: Optional[int] = Field(None, description="K/D difference")
    kast: Optional[float] = Field(None, description="KAST percentage")
    adr: Optional[float] = Field(None, description="Average damage per round")
    hs_pct: Optional[float] = Field(None, description="Headshot percentage")
    fk: Optional[int] = Field(None, description="First kills")
    fd: Optional[int] = Field(None, description="First deaths")
    fk_diff: Optional[int] = Field(None, description="First kill difference")


class MapTeamScore(BaseModel):
    """Team score for a specific map."""
    
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = Field(None, description="Team ID")
    name: Optional[str] = Field(None, description="Team name")
    short: Optional[str] = Field(None, description="Team short tag")
    score: Optional[int] = Field(None, description="Map score")
    attacker_rounds: Optional[int] = Field(None, description="Rounds won as attacker")
    defender_rounds: Optional[int] = Field(None, description="Rounds won as defender")
    is_winner: bool = Field(description="Whether team won the map")


class RoundResult(BaseModel):
    """Single round result."""
    
    model_config = ConfigDict(frozen=True)
    
    number: int = Field(description="Round number")
    winner_side: Optional[str] = Field(None, description="Winning side (Attacker/Defender)")
    method: Optional[str] = Field(None, description="Win method")
    score: Optional[Tuple[int, int]] = Field(None, description="Cumulative score")
    winner_team_id: Optional[int] = Field(None, description="Winning team ID")
    winner_team_short: Optional[str] = Field(None, description="Winning team short tag")
    winner_team_name: Optional[str] = Field(None, description="Winning team name")


class MapPlayers(BaseModel):
    """Map statistics with player data."""
    
    model_config = ConfigDict(frozen=True)
    
    game_id: Optional[int] = Field(None, description="Game ID")
    map_name: Optional[str] = Field(None, description="Map name")
    players: List[PlayerStats] = Field(default_factory=list, description="Player statistics")
    teams: Optional[Tuple[MapTeamScore, MapTeamScore]] = Field(None, description="Team scores")
    rounds: Optional[List[RoundResult]] = Field(None, description="Round-by-round results")


_METHOD_LABELS: Dict[str, str] = {
    "elim": "Elimination",
    "elimination": "Elimination",
    "defuse": "SpikeDefused",
    "defused": "SpikeDefused",
    "boom": "SpikeExplosion",
    "explode": "SpikeExplosion",
    "explosion": "SpikeExplosion",
    "time": "TimeRunOut",
    "timer": "TimeRunOut",
}


def _fetch_team_meta(team_id: int, timeout: float) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Fetch team metadata (short tag, country, country code)."""
    try:
        url = f"{VLR_BASE}/team/{team_id}"
        html = fetch_html(url, timeout)
        soup = BeautifulSoup(html, "lxml")
        
        short_tag = extract_text(soup.select_one(".team-header .team-header-tag"))
        country_el = soup.select_one(".team-header .team-header-country")
        country = extract_text(country_el) if country_el else None
        
        flag = None
        if country_el:
            flag_icon = country_el.select_one(".flag")
            if flag_icon:
                for cls in flag_icon.get("class", []):
                    if cls.startswith("mod-") and cls != "mod-dark":
                        flag = cls.removeprefix("mod-")
                        break
        
        return short_tag or None, country, flag
    except Exception:
        return None, None, None


def _parse_note_for_picks_bans(
    note_text: str,
    team1_aliases: List[str],
    team2_aliases: List[str],
) -> Tuple[List[MapAction], List[MapAction], List[MapAction], Optional[str]]:
    """Parse picks/bans from header note text."""
    text = re.sub(r"\s+", " ", note_text).strip()
    picks: List[MapAction] = []
    bans: List[MapAction] = []
    remaining: Optional[str] = None
    
    action_re = re.compile(r"([^;]+?)\s+(ban|pick)\s+([^;]+?)(?:;|$)", re.IGNORECASE)
    
    def normalize_team(who: str) -> str:
        who_clean = who.strip()
        for aliases in (team1_aliases, team2_aliases):
            for alias in aliases:
                if alias and alias.lower() in who_clean.lower():
                    return aliases[0]
        return who_clean
    
    ordered_actions: List[MapAction] = []
    for m in action_re.finditer(text):
        who = m.group(1).strip()
        action = m.group(2).lower()
        game_map = m.group(3).strip()
        canonical = normalize_team(who)
        map_action = MapAction(action=action, team=canonical, map=game_map)
        ordered_actions.append(map_action)
        if action == "ban":
            bans.append(map_action)
        else:
            picks.append(map_action)
    
    rem_m = re.search(r"([^;]+?)\s+remains\b", text, re.IGNORECASE)
    if rem_m:
        remaining = rem_m.group(1).strip()
    
    return ordered_actions, picks, bans, remaining

def info(match_id: int, timeout: float = DEFAULT_TIMEOUT) -> Optional[Info]:
    """
    Get series information.
    
    Args:
        match_id: Match ID
        timeout: Request timeout in seconds
    
    Returns:
        Series information or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> info = vlr.series.info(match_id=12345)
        >>> print(f"{info.teams[0].name} vs {info.teams[1].name}")
        >>> print(f"Score: {info.score[0]}-{info.score[1]}")
    """
    url = f"{VLR_BASE}/{match_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".wf-card.match-header")
    if not header:
        return None
    
    # Event name and phase
    event_name = extract_text(header.select_one(".match-header-event div[style*='font-weight']")) or \
                 extract_text(header.select_one(".match-header-event .wf-title-med"))
    event_phase = re.sub(r"\s+", " ", extract_text(header.select_one(".match-header-event-series"))).strip()
    
    # Date and time
    date_el = header.select_one(".match-header-date .moment-tz-convert")
    match_date: Optional[datetime.date] = None
    time_value: Optional[datetime.time] = None
    
    if date_el and date_el.has_attr("data-utc-ts"):
        try:
            dt = datetime.datetime.strptime(date_el["data-utc-ts"], "%Y-%m-%d %H:%M:%S")
            match_date = dt.date()
        except Exception:
            pass
    
    time_els = header.select(".match-header-date .moment-tz-convert")
    if len(time_els) >= 2:
        raw = extract_text(time_els[1])
        m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)\s*([+\-])(\d{2})$", raw, re.IGNORECASE)
        if m:
            hour = int(m.group(1)) % 12
            minute = int(m.group(2))
            if m.group(3).upper() == "PM":
                hour += 12
            sign = 1 if m.group(4) == "+" else -1
            offset_hours = int(m.group(5))
            tz = datetime.timezone(sign * datetime.timedelta(hours=offset_hours))
            time_value = datetime.time(hour=hour, minute=minute, tzinfo=tz)
    
    # Teams and scores
    t1_link = header.select_one(".match-header-link.mod-1")
    t2_link = header.select_one(".match-header-link.mod-2")
    t1 = extract_text(header.select_one(".match-header-link.mod-1 .wf-title-med"))
    t2 = extract_text(header.select_one(".match-header-link.mod-2 .wf-title-med"))
    t1_id = extract_id_from_url(t1_link.get("href") if t1_link else None, "team")
    t2_id = extract_id_from_url(t2_link.get("href") if t2_link else None, "team")
    
    t1_short, t1_country, t1_country_code = None, None, None
    t2_short, t2_country, t2_country_code = None, None, None
    
    if t1_id:
        t1_short, t1_country, t1_country_code = _fetch_team_meta(t1_id, timeout)
    if t2_id:
        t2_short, t2_country, t2_country_code = _fetch_team_meta(t2_id, timeout)
    
    s1 = header.select_one(".match-header-vs-score-winner")
    s2 = header.select_one(".match-header-vs-score-loser")
    raw_score: Tuple[Optional[int], Optional[int]] = (None, None)
    try:
        if s1 and s2:
            raw_score = (int(extract_text(s1)), int(extract_text(s2)))
    except ValueError:
        pass
    
    notes = header.select(".match-header-vs-note")
    status_note = extract_text(notes[0]) if notes else ""
    best_of = extract_text(notes[1]) if len(notes) > 1 else None
    
    # Picks/bans
    team1_info = TeamInfo(
        id=t1_id,
        name=t1,
        short=t1_short,
        country=t1_country,
        country_code=t1_country_code,
        score=raw_score[0],
    )
    team2_info = TeamInfo(
        id=t2_id,
        name=t2,
        short=t2_short,
        country=t2_country,
        country_code=t2_country_code,
        score=raw_score[1],
    )
    
    header_note_node = header.select_one(".match-header-note")
    header_note_text = extract_text(header_note_node)
    
    aliases1 = [alias for alias in (team1_info.short, team1_info.name) if alias]
    aliases2 = [alias for alias in (team2_info.short, team2_info.name) if alias]
    
    map_actions, picks, bans, remaining = _parse_note_for_picks_bans(
        header_note_text,
        aliases1 or [team1_info.name],
        aliases2 or [team2_info.name],
    )
    
    return Info(
        match_id=match_id,
        teams=(team1_info, team2_info),
        score=raw_score,
        status_note=status_note.lower(),
        best_of=best_of,
        event=event_name,
        event_phase=event_phase,
        date=match_date,
        time=time_value,
        map_actions=map_actions,
        picks=picks,
        bans=bans,
        remaining=remaining,
    )


def matches(series_id: int, limit: Optional[int] = None, timeout: float = DEFAULT_TIMEOUT) -> List[MapPlayers]:
    """
    Get detailed match statistics for a series.
    
    Args:
        series_id: Series/match ID
        limit: Maximum number of maps to return (optional)
        timeout: Request timeout in seconds
    
    Returns:
        List of map statistics with player data
    
    Example:
        >>> import vlrdevapi as vlr
        >>> maps = vlr.series.matches(series_id=12345, limit=3)
        >>> for map_data in maps:
        ...     print(f"Map: {map_data.map_name}")
        ...     for player in map_data.players:
        ...         print(f"  {player.name}: {player.acs} ACS")
    """
    url = f"{VLR_BASE}/{series_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    stats_root = soup.select_one(".vm-stats")
    if not stats_root:
        return []
    
    # Build game_id -> map name from tabs
    game_name_map: Dict[int, str] = {}
    for nav in stats_root.select("[data-game-id]"):
        classes = nav.get("class", [])
        if any("vm-stats-game" in c for c in classes):
            continue
        gid = nav.get("data-game-id")
        if not gid or not gid.isdigit():
            continue
        txt = nav.get_text(" ", strip=True)
        if not txt:
            continue
        name = re.sub(r"^\s*\d+\s*", "", txt).strip()
        game_name_map[int(gid)] = name
    
    # Map team identity
    short_to_id: Dict[str, int] = {}
    
    # Determine order from nav
    ordered_ids: List[str] = []
    nav_items = list(stats_root.select(".vm-stats-gamesnav .vm-stats-gamesnav-item"))
    if nav_items:
        temp_ids: List[str] = []
        for item in nav_items:
            gid = item.get("data-game-id")
            if gid:
                temp_ids.append(gid)
        has_all = any(g == "all" for g in temp_ids)
        numeric_ids: List[Tuple[int, str]] = []
        for g in temp_ids:
            if g != "all" and g.isdigit():
                try:
                    numeric_ids.append((int(g), g))
                except Exception:
                    continue
        numeric_ids.sort(key=lambda x: x[0])
        ordered_ids = (["all"] if has_all else []) + [g for _, g in numeric_ids]
    
    if not ordered_ids:
        ordered_ids = [g.get("data-game-id") or "" for g in stats_root.select(".vm-stats-game")]
    
    result: List[MapPlayers] = []
    section_by_id: Dict[str, any] = {(g.get("data-game-id") or ""): g for g in stats_root.select(".vm-stats-game")}
    
    for gid_raw in ordered_ids:
        if limit is not None and len(result) >= limit:
            break
        game = section_by_id.get(gid_raw)
        if game is None:
            continue
        
        game_id = game.get("data-game-id")
        gid = None
        try:
            gid = int(game_id) if game_id and game_id.isdigit() else None
        except Exception:
            gid = None
        
        if game_id == "all":
            map_name = "All"
        else:
            map_name = game_name_map.get(gid) if gid is not None else None
        
        if not map_name:
            header = game.select_one(".vm-stats-game-header .map")
            if header:
                outer = header.select_one("span")
                if outer:
                    direct = outer.find(string=True, recursive=False)
                    map_name = (direct or "").strip() or None
        
        # Parse players (simplified - full implementation would parse table)
        players: List[PlayerStats] = []
        
        result.append(MapPlayers(
            game_id=gid,
            map_name=map_name,
            players=players,
            teams=None,
            rounds=None,
        ))
    
    return result
