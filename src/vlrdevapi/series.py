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
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import extract_text, parse_int, parse_float, extract_id_from_url

# Pre-compiled regex patterns for performance
_WHITESPACE_RE = re.compile(r"\s+")
_PICKS_BANS_RE = re.compile(r"([^;]+?)\s+(ban|pick)\s+([^;]+?)(?:;|$)", re.IGNORECASE)
_REMAINS_RE = re.compile(r"([^;]+?)\s+remains\b", re.IGNORECASE)
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)\s*([A-Z]{2,4}|[+\-]\d{2})?", re.IGNORECASE)
_MAP_NUMBER_RE = re.compile(r"^\s*\d+\s*")

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
    patch: Optional[str] = Field(None, description="Game patch / version")
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
    
    game_id: Optional[int | str] = Field(None, description="Game ID (int for specific maps, 'All' for aggregate)")
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


def _fetch_team_meta_batch(team_ids: List[int], timeout: float) -> Dict[int, Tuple[Optional[str], Optional[str], Optional[str]]]:
    """Fetch team metadata for multiple teams concurrently.
    
    Args:
        team_ids: List of team IDs
        timeout: Request timeout
    
    Returns:
        Dictionary mapping team_id to (short_tag, country, country_code)
    """
    if not team_ids:
        return {}
    
    # Build URLs for all teams
    urls = [f"{VLR_BASE}/team/{team_id}" for team_id in team_ids]
    
    # Batch fetch all team pages concurrently
    batch_results = batch_fetch_html(urls, timeout=timeout, max_workers=min(2, len(urls)))
    
    # Parse metadata from each page
    results: Dict[int, Tuple[Optional[str], Optional[str], Optional[str]]] = {}
    
    for team_id, url in zip(team_ids, urls):
        html = batch_results.get(url)
        
        if isinstance(html, Exception) or not html:
            results[team_id] = (None, None, None)
            continue
        
        try:
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
            
            results[team_id] = (short_tag or None, country, flag)
        except Exception:
            results[team_id] = (None, None, None)
    
    return results


def _parse_note_for_picks_bans(
    note_text: str,
    team1_aliases: List[str],
    team2_aliases: List[str],
) -> Tuple[List[MapAction], List[MapAction], List[MapAction], Optional[str]]:
    """Parse picks/bans from header note text."""
    text = _WHITESPACE_RE.sub(" ", note_text).strip()
    picks: List[MapAction] = []
    bans: List[MapAction] = []
    remaining: Optional[str] = None
    
    def normalize_team(who: str) -> str:
        who_clean = who.strip()
        for aliases in (team1_aliases, team2_aliases):
            for alias in aliases:
                if alias and alias.lower() in who_clean.lower():
                    return aliases[0]
        return who_clean
    
    ordered_actions: List[MapAction] = []
    for m in _PICKS_BANS_RE.finditer(text):
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
    
    rem_m = _REMAINS_RE.search(text)
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
    event_phase = _WHITESPACE_RE.sub(" ", extract_text(header.select_one(".match-header-event-series"))).strip()
    
    # Date, time, and patch information
    date_el = header.select_one(".match-header-date .moment-tz-convert")
    match_date: Optional[datetime.date] = None
    time_value: Optional[datetime.time] = None
    patch_text: Optional[str] = None
    
    if date_el and date_el.has_attr("data-utc-ts"):
        try:
            dt = datetime.datetime.strptime(date_el["data-utc-ts"], "%Y-%m-%d %H:%M:%S")
            match_date = dt.date()
        except Exception:
            pass
    
    time_els = header.select(".match-header-date .moment-tz-convert")
    if len(time_els) >= 2:
        time_node = time_els[1]
        dt_attr = time_node.get("data-utc-ts")
        if dt_attr:
            try:
                dt_parsed = datetime.datetime.strptime(dt_attr, "%Y-%m-%d %H:%M:%S")
                tz_utc = datetime.timezone.utc
                time_value = datetime.time(hour=dt_parsed.hour, minute=dt_parsed.minute, tzinfo=tz_utc)
            except Exception:
                pass
        if time_value is None:
            raw = extract_text(time_node)
            # Handles formats like "2:00 PM PST" and "2:00 PM +02"
            m = _TIME_RE.match(raw)
            if m:
                hour = int(m.group(1)) % 12
                minute = int(m.group(2))
                if m.group(3).upper() == "PM":
                    hour += 12
                tzinfo = None
                suffix = m.group(4)
                if suffix and suffix.startswith(("+", "-")) and len(suffix) == 3:
                    sign = 1 if suffix[0] == "+" else -1
                    offset_hours = int(suffix[1:])
                    tzinfo = datetime.timezone(sign * datetime.timedelta(hours=offset_hours))
                else:
                    tzinfo = datetime.timezone.utc if dt_attr else None
                time_value = datetime.time(hour=hour, minute=minute, tzinfo=tzinfo)
    patch_el = header.select_one(".match-header-date div[style*='font-style: italic']")
    if patch_el:
        patch_text = extract_text(patch_el) or None
    
    # Teams and scores
    t1_link = header.select_one(".match-header-link.mod-1")
    t2_link = header.select_one(".match-header-link.mod-2")
    t1 = extract_text(header.select_one(".match-header-link.mod-1 .wf-title-med"))
    t2 = extract_text(header.select_one(".match-header-link.mod-2 .wf-title-med"))
    t1_id = extract_id_from_url(t1_link.get("href") if t1_link else None, "team")
    t2_id = extract_id_from_url(t2_link.get("href") if t2_link else None, "team")
    
    t1_short, t1_country, t1_country_code = None, None, None
    t2_short, t2_country, t2_country_code = None, None, None
    
    # Batch fetch team metadata for both teams concurrently
    team_ids_to_fetch = [tid for tid in [t1_id, t2_id] if tid is not None]
    if team_ids_to_fetch:
        team_meta_map = _fetch_team_meta_batch(team_ids_to_fetch, timeout)
        if t1_id:
            t1_short, t1_country, t1_country_code = team_meta_map.get(t1_id, (None, None, None))
        if t2_id:
            t2_short, t2_country, t2_country_code = team_meta_map.get(t2_id, (None, None, None))
    
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
        patch=patch_text,
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
        name = _MAP_NUMBER_RE.sub("", txt).strip()
        game_name_map[int(gid)] = name
    
    def canonical(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return _WHITESPACE_RE.sub(" ", value).strip().lower()
    
    # Fetch team metadata to map names/shorts to IDs
    series_details = info(series_id, timeout=timeout)
    team_meta_lookup: Dict[str, Dict[str, Optional[str | int]]] = {}
    team_short_to_id: Dict[str, Optional[int]] = {}
    if series_details:
        for team_info in series_details.teams:
            meta = {
                "id": team_info.id,
                "name": team_info.name,
                "short": team_info.short,
            }
            for key in filter(None, [team_info.name, team_info.short]):
                canon = canonical(key)
                if canon:
                    team_meta_lookup[canon] = meta
            if team_info.short:
                team_short_to_id[team_info.short.upper()] = team_info.id
    
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
        gid: Optional[int | str] = None
        
        if game_id == "all":
            gid = "All"
            map_name = "All"
        else:
            try:
                gid = int(game_id) if game_id and game_id.isdigit() else None
            except Exception:
                gid = None
            map_name = game_name_map.get(gid) if gid is not None else None
        
        if not map_name:
            header = game.select_one(".vm-stats-game-header .map")
            if header:
                outer = header.select_one("span")
                if outer:
                    direct = outer.find(string=True, recursive=False)
                    map_name = (direct or "").strip() or None
        
        # Parse teams from header
        teams_tuple: Optional[Tuple[MapTeamScore, MapTeamScore]] = None
        header = game.select_one(".vm-stats-game-header")
        if header:
            team_divs = header.select(".team")
            if len(team_divs) >= 2:
                # Team 1
                t1_name_el = team_divs[0].select_one(".team-name")
                t1_name = extract_text(t1_name_el) if t1_name_el else None
                t1_score_el = team_divs[0].select_one(".score")
                t1_score = parse_int(extract_text(t1_score_el)) if t1_score_el else None
                t1_is_winner = t1_score_el and "mod-win" in (t1_score_el.get("class") or []) if t1_score_el else False
                
                # Parse attacker/defender rounds for team 1
                t1_ct = team_divs[0].select_one(".mod-ct")
                t1_t = team_divs[0].select_one(".mod-t")
                t1_ct_rounds = parse_int(extract_text(t1_ct)) if t1_ct else None
                t1_t_rounds = parse_int(extract_text(t1_t)) if t1_t else None
                
                # Team 2
                t2_name_el = team_divs[1].select_one(".team-name")
                t2_name = extract_text(t2_name_el) if t2_name_el else None
                t2_score_el = team_divs[1].select_one(".score")
                t2_score = parse_int(extract_text(t2_score_el)) if t2_score_el else None
                t2_is_winner = t2_score_el and "mod-win" in (t2_score_el.get("class") or []) if t2_score_el else False
                
                # Parse attacker/defender rounds for team 2
                t2_ct = team_divs[1].select_one(".mod-ct")
                t2_t = team_divs[1].select_one(".mod-t")
                t2_ct_rounds = parse_int(extract_text(t2_ct)) if t2_ct else None
                t2_t_rounds = parse_int(extract_text(t2_t)) if t2_t else None
                
                if t1_name and t2_name:
                    t1_meta = team_meta_lookup.get(canonical(t1_name))
                    t2_meta = team_meta_lookup.get(canonical(t2_name))
                    teams_tuple = (
                        MapTeamScore(
                            id=t1_meta.get("id") if t1_meta else None,
                            name=t1_name,
                            short=t1_meta.get("short") if t1_meta else None,
                            score=t1_score,
                            attacker_rounds=t1_t_rounds,
                            defender_rounds=t1_ct_rounds,
                            is_winner=t1_is_winner,
                        ),
                        MapTeamScore(
                            id=t2_meta.get("id") if t2_meta else None,
                            name=t2_name,
                            short=t2_meta.get("short") if t2_meta else None,
                            score=t2_score,
                            attacker_rounds=t2_t_rounds,
                            defender_rounds=t2_ct_rounds,
                            is_winner=t2_is_winner,
                        ),
                    )
        
        # Parse rounds
        rounds_list: List[RoundResult] = []
        rounds_container = game.select_one(".vlr-rounds")
        if rounds_container:
            round_rows = rounds_container.select(".vlr-rounds-row")
            # Determine top/bottom team order from the rounds legend
            round_team_names: List[str] = []
            if round_rows:
                header_col = round_rows[0].select_one(".vlr-rounds-row-col")
                if header_col:
                    round_team_names = [extract_text(team_el) for team_el in header_col.select(".team")]
            # Flatten all round columns across rows, skipping headers/spacing
            flat_columns: List = []
            for row in round_rows:
                for col in row.select(".vlr-rounds-row-col"):
                    if col.select_one(".team"):
                        continue
                    if "mod-spacing" in (col.get("class") or []):
                        continue
                    flat_columns.append(col)
            prev_score: Optional[Tuple[int, int]] = None
            final_score_tuple: Optional[Tuple[int, int]] = None
            if teams_tuple and all(ts.score is not None for ts in teams_tuple):
                final_score_tuple = (teams_tuple[0].score or 0, teams_tuple[1].score or 0)
            for col in flat_columns:
                rnd_num_el = col.select_one(".rnd-num")
                if not rnd_num_el:
                    continue
                rnd_num = parse_int(extract_text(rnd_num_el))
                if rnd_num is None:
                    continue
                title = (col.get("title") or "").strip()
                if not title and not col.select_one(".rnd-sq.mod-win"):
                    # No data beyond this point
                    break
                score_tuple: Optional[Tuple[int, int]] = None
                if "-" in title:
                    parts = title.split("-")
                    if len(parts) == 2:
                        s1 = parse_int(parts[0].strip())
                        s2 = parse_int(parts[1].strip())
                        if s1 is not None and s2 is not None:
                            score_tuple = (s1, s2)
                # Determine winning square and method
                winner_sq = col.select_one(".rnd-sq.mod-win")
                winner_side = None
                method = None
                if winner_sq:
                    classes = winner_sq.get("class") or []
                    if "mod-t" in classes:
                        winner_side = "Attacker"
                    elif "mod-ct" in classes:
                        winner_side = "Defender"
                    method_img = winner_sq.select_one("img")
                    if method_img:
                        src = (method_img.get("src") or "").lower()
                        if "elim" in src:
                            method = "Elimination"
                        elif "defuse" in src:
                            method = "SpikeDefused"
                        elif "boom" in src or "explosion" in src:
                            method = "SpikeExplosion"
                        elif "time" in src:
                            method = "TimeRunOut"
                winner_idx: Optional[int] = None
                if score_tuple is not None:
                    if prev_score is None:
                        winner_idx = 0 if score_tuple[0] > score_tuple[1] else 1 if score_tuple[1] > score_tuple[0] else None
                    else:
                        if score_tuple[0] > prev_score[0]:
                            winner_idx = 0
                        elif score_tuple[1] > prev_score[1]:
                            winner_idx = 1
                    prev_score = score_tuple
                winner_team_id = None
                winner_team_short = None
                winner_team_name = None
                if winner_idx is not None and teams_tuple and 0 <= winner_idx < len(teams_tuple):
                    team_score = teams_tuple[winner_idx]
                    winner_team_id = team_score.id
                    winner_team_short = team_score.short
                    winner_team_name = team_score.name
                elif winner_idx is not None and round_team_names:
                    team_name = round_team_names[winner_idx] if winner_idx < len(round_team_names) else None
                    if team_name:
                        meta = team_meta_lookup.get(canonical(team_name))
                        if meta:
                            winner_team_id = meta.get("id")  # type: ignore[attr-defined]
                            winner_team_short = meta.get("short")  # type: ignore[attr-defined]
                            winner_team_name = meta.get("name")  # type: ignore[attr-defined]
                        else:
                            winner_team_name = team_name
                rounds_list.append(RoundResult(
                    number=rnd_num,
                    winner_side=winner_side,
                    method=method,
                    score=score_tuple,
                    winner_team_id=winner_team_id,
                    winner_team_short=winner_team_short,
                    winner_team_name=winner_team_name,
                ))
                if final_score_tuple and score_tuple == final_score_tuple:
                    break
        
        # Helpers for player parsing
        def extract_mod_both(cell) -> Optional[str]:
            if not cell:
                return None
            # Prefer spans containing mod-both
            for selector in [".side.mod-both", ".side.mod-side.mod-both", ".mod-both"]:
                el = cell.select_one(selector)
                if el:
                    return extract_text(el)
            for el in cell.select("span"):
                classes = el.get("class", [])
                if classes and any("mod-both" in cls for cls in classes):
                    return extract_text(el)
            return extract_text(cell)
        
        def parse_numeric(text: Optional[str]) -> Optional[float]:
            if not text:
                return None
            cleaned = text.strip().replace(",", "")
            if not cleaned:
                return None
            sign = 1
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            elif cleaned.startswith("-"):
                sign = -1
                cleaned = cleaned[1:]
            percent = cleaned.endswith("%")
            if percent:
                cleaned = cleaned[:-1]
            cleaned = cleaned.strip()
            if not cleaned:
                return None
            try:
                value = float(cleaned)
            except ValueError:
                return None
            return sign * value
        
        # Parse players from both team tables
        players: List[PlayerStats] = []
        tables = game.select("table.wf-table-inset")
        team_scores = list(teams_tuple) if teams_tuple else []
        for table_idx, table in enumerate(tables):
            tbody = table.select_one("tbody")
            if not tbody:
                continue
            team_score = team_scores[table_idx] if table_idx < len(team_scores) else None
            team_meta = None
            if team_score:
                team_meta = team_meta_lookup.get(canonical(team_score.name))
            inferred_team_short = team_meta.get("short") if team_meta else (team_score.short if team_score else None)
            inferred_team_id = team_meta.get("id") if team_meta else (team_score.id if team_score else None)
            for row in tbody.select("tr"):
                player_cell = row.select_one(".mod-player")
                if not player_cell:
                    continue
                player_link = player_cell.select_one("a[href*='/player/']")
                if not player_link:
                    continue
                player_id = extract_id_from_url(player_link.get("href", ""), "player")
                name_el = player_link.select_one(".text-of")
                name = extract_text(name_el) if name_el else None
                if not name:
                    continue
                team_short_el = player_link.select_one(".ge-text-light")
                player_team_short = extract_text(team_short_el) if team_short_el else inferred_team_short
                if player_team_short:
                    player_team_short = player_team_short.strip().upper()
                team_id = None
                if player_team_short:
                    team_id = team_short_to_id.get(player_team_short.upper(), inferred_team_id)
                elif inferred_team_id is not None:
                    team_id = inferred_team_id
                # Country
                flag = player_cell.select_one(".flag")
                country = None
                if flag:
                    for cls in flag.get("class", []):
                        if cls.startswith("mod-") and cls != "mod-dark":
                            country_code = cls.removeprefix("mod-")
                            country = COUNTRY_MAP.get(country_code.upper(), country_code.upper())
                            break
                # Agents
                agents: List[str] = []
                agents_cell = row.select_one(".mod-agents")
                if agents_cell:
                    for img in agents_cell.select("img"):
                        agent_name = img.get("title") or img.get("alt", "")
                        if agent_name:
                            agents.append(agent_name)
                # Stats
                stat_cells = row.select(".mod-stat")
                values = [parse_numeric(extract_mod_both(cell)) for cell in stat_cells]
                def as_int(idx: int) -> Optional[int]:
                    if idx >= len(values) or values[idx] is None:
                        return None
                    return int(values[idx])
                def as_float(idx: int) -> Optional[float]:
                    if idx >= len(values) or values[idx] is None:
                        return None
                    return float(values[idx])
                r_float = as_float(0)
                acs_int = as_int(1)
                k_int = as_int(2)
                d_int = as_int(3)
                a_int = as_int(4)
                kd_diff_int = as_int(5)
                kast_float = as_float(6)
                adr_float = as_float(7)
                hs_pct_float = as_float(8)
                fk_int = as_int(9)
                fd_int = as_int(10)
                fk_diff_int = as_int(11)
                players.append(PlayerStats(
                    country=country,
                    name=name,
                    team_short=player_team_short,
                    team_id=team_id,
                    player_id=player_id,
                    agents=agents,
                    r=r_float,
                    acs=acs_int,
                    k=k_int,
                    d=d_int,
                    a=a_int,
                    kd_diff=kd_diff_int,
                    kast=kast_float,
                    adr=adr_float,
                    hs_pct=hs_pct_float,
                    fk=fk_int,
                    fd=fd_int,
                    fk_diff=fk_diff_int,
                ))
        result.append(MapPlayers(
            game_id=gid,
            map_name=map_name,
            players=players,
            teams=teams_tuple,
            rounds=rounds_list if rounds_list else None,
        ))
    
    return result
