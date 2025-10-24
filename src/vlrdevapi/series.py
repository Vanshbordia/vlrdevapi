"""Series/match-related API endpoints and models."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from bs4.element import Tag

from .config import get_config
from .countries import COUNTRY_MAP
from .fetcher import fetch_html, batch_fetch_html
from .exceptions import NetworkError
from .utils import extract_text, parse_int, extract_id_from_url

_config = get_config()

# Pre-compiled regex patterns for performance
_WHITESPACE_RE = re.compile(r"\s+")
_PICKS_BANS_RE = re.compile(r"([^;]+?)\s+(ban|pick)\s+([^;]+?)(?:;|$)", re.IGNORECASE)
_REMAINS_RE = re.compile(r"([^;]+?)\s+remains\b", re.IGNORECASE)
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)\s*([A-Z]{2,4}|[+\-]\d{2})?", re.IGNORECASE)
_MAP_NUMBER_RE = re.compile(r"^\s*\d+\s*")

@dataclass(frozen=True)
class TeamInfo:
    """Team information in a series."""

    name: str
    id: int | None = None
    short: str | None = None
    country: str | None = None
    country_code: str | None = None
    score: int | None = None


@dataclass(frozen=True)
class MapAction:
    """Map pick/ban action."""

    action: str
    team: str
    map: str


@dataclass(frozen=True)
class Info:
    """Series information."""

    match_id: int
    teams: tuple["TeamInfo", "TeamInfo"]
    score: tuple[int | None, int | None]
    status_note: str
    event: str
    event_phase: str
    best_of: str | None = None
    date: datetime.date | None = None
    time: datetime.time | None = None
    patch: str | None = None
    map_actions: list["MapAction"] = field(default_factory=list)
    picks: list["MapAction"] = field(default_factory=list)
    bans: list["MapAction"] = field(default_factory=list)
    remaining: str | None = None


@dataclass(frozen=True)
class PlayerStats:
    """Player statistics in a map."""

    name: str
    country: str | None = None
    team_short: str | None = None
    team_id: int | None = None
    player_id: int | None = None
    agents: list[str] = field(default_factory=list)
    r: float | None = None
    acs: int | None = None
    k: int | None = None
    d: int | None = None
    a: int | None = None
    kd_diff: int | None = None
    kast: float | None = None
    adr: float | None = None
    hs_pct: float | None = None
    fk: int | None = None
    fd: int | None = None
    fk_diff: int | None = None


@dataclass(frozen=True)
class MapTeamScore:
    """Team score for a specific map."""

    is_winner: bool
    id: int | None = None
    name: str | None = None
    short: str | None = None
    score: int | None = None
    attacker_rounds: int | None = None
    defender_rounds: int | None = None


@dataclass(frozen=True)
class RoundResult:
    """Single round result."""

    number: int
    winner_side: str | None = None
    method: str | None = None
    score: tuple[int, int] | None = None
    winner_team_id: int | None = None
    winner_team_short: str | None = None
    winner_team_name: str | None = None


@dataclass(frozen=True)
class MapPlayers:
    """Map statistics with player data."""

    game_id: int | str | None = None
    map_name: str | None = None
    players: list["PlayerStats"] = field(default_factory=list)
    teams: tuple["MapTeamScore", "MapTeamScore"] | None = None
    rounds: list["RoundResult"] | None = None


_METHOD_LABELS: dict[str, str] = {
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


def _fetch_team_meta_batch(team_ids: list[int], timeout: float) -> dict[int, tuple[str | None, str | None, str | None]]:
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
    urls = [f"{_config.vlr_base}/team/{team_id}" for team_id in team_ids]
    
    # Batch fetch all team pages concurrently
    batch_results = batch_fetch_html(urls, timeout=timeout, max_workers=min(2, len(urls)))
    
    # Parse metadata from each page
    results: dict[int, tuple[str | None, str | None, str | None]] = {}
    
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
                    classes_val = flag_icon.get("class")
                    flag_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                    for cls in flag_classes:
                        if cls.startswith("mod-") and cls != "mod-dark":
                            flag = cls.removeprefix("mod-")
                            break
            
            results[team_id] = (short_tag or None, country, flag)
        except Exception:
            results[team_id] = (None, None, None)
    
    return results


def _parse_note_for_picks_bans(
    note_text: str,
    team1_aliases: list[str],
    team2_aliases: list[str],
) -> tuple[list[MapAction], list[MapAction], list[MapAction], str | None]:
    """Parse picks/bans from header note text."""
    text = _WHITESPACE_RE.sub(" ", note_text).strip()
    picks: list[MapAction] = []
    bans: list[MapAction] = []
    remaining: str | None = None
    
    def normalize_team(who: str) -> str:
        who_clean = who.strip()
        for aliases in (team1_aliases, team2_aliases):
            for alias in aliases:
                if alias and alias.lower() in who_clean.lower():
                    return aliases[0]
        return who_clean
    
    ordered_actions: list[MapAction] = []
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

def info(match_id: int, timeout: float | None = None) -> Info | None:
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
    url = f"{_config.vlr_base}/{match_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
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
    match_date: datetime.date | None = None
    time_value: datetime.time | None = None
    patch_text: str | None = None
    
    if date_el and date_el.has_attr("data-utc-ts"):
        try:
            dt_attr = date_el.get("data-utc-ts")
            dt_str = dt_attr if isinstance(dt_attr, str) else None
            if dt_str:
                dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                match_date = dt.date()
        except Exception:
            pass
    
    time_els = header.select(".match-header-date .moment-tz-convert")
    if len(time_els) >= 2:
        time_node = time_els[1]
        dt_attr = time_node.get("data-utc-ts")
        dt_str = dt_attr if isinstance(dt_attr, str) else None
        if dt_str:
            try:
                dt_parsed = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
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
    t1_href = t1_link.get("href") if t1_link else None
    t2_href = t2_link.get("href") if t2_link else None
    t1_href = t1_href if isinstance(t1_href, str) else None
    t2_href = t2_href if isinstance(t2_href, str) else None
    t1_id = extract_id_from_url(t1_href, "team")
    t2_id = extract_id_from_url(t2_href, "team")
    
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
    raw_score: tuple[int | None, int | None] = (None, None)
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


def matches(series_id: int, limit: int | None = None, timeout: float | None = None) -> list[MapPlayers]:
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
    url = f"{_config.vlr_base}/{series_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    stats_root = soup.select_one(".vm-stats")
    if not stats_root:
        return []
    
    # Build game_id -> map name from tabs
    game_name_map: dict[int, str] = {}
    for nav in stats_root.select("[data-game-id]"):
        classes_val = nav.get("class")
        nav_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
        if any("vm-stats-game" in c for c in nav_classes):
            continue
        
        gid_val = nav.get("data-game-id")
        gid = gid_val if isinstance(gid_val, str) else None
        if not gid or not gid.isdigit():
            continue
        txt = nav.get_text(" ", strip=True)
        if not txt:
            continue
        name = _MAP_NUMBER_RE.sub("", txt).strip()
        game_name_map[int(gid)] = name
    
    def canonical(value: str | None) -> str | None:
        if not value:
            return None
        return _WHITESPACE_RE.sub(" ", value).strip().lower()
    
    # Fetch team metadata to map names/shorts to IDs
    series_details = info(series_id, timeout=timeout)
    team_meta_lookup: dict[str, dict[str, str | int | None]] = {}
    team_short_to_id: dict[str, int | None] = {}
    if series_details:
        for team_info in series_details.teams:
            team_meta_rec: dict[str, str | int | None] = {"id": team_info.id, "name": team_info.name, "short": team_info.short}
            for key in filter(None, [team_info.name, team_info.short]):
                canon = canonical(key)
                if canon is not None:
                    team_meta_lookup[canon] = team_meta_rec
            if team_info.short:
                team_short_to_id[team_info.short.upper()] = team_info.id
    
    # Determine order from nav
    ordered_ids: list[str] = []
    nav_items = list(stats_root.select(".vm-stats-gamesnav .vm-stats-gamesnav-item"))
    if nav_items:
        temp_ids: list[str] = []
        for item in nav_items:
            gid_val = item.get("data-game-id")
            gid = gid_val if isinstance(gid_val, str) else None
            if gid:
                temp_ids.append(gid)
        has_all = any(g == "all" for g in temp_ids)
        numeric_ids: list[tuple[int, str]] = []
        for g in temp_ids:
            if g != "all" and g.isdigit():
                try:
                    numeric_ids.append((int(g), g))
                except Exception:
                    continue
        numeric_ids.sort(key=lambda x: x[0])
        ordered_ids = (["all"] if has_all else []) + [g for _, g in numeric_ids]
    
    if not ordered_ids:
        ordered_ids = []
        for g in stats_root.select(".vm-stats-game"):
            val = g.get("data-game-id")
            s = val if isinstance(val, str) else None
            ordered_ids.append(s or "")
    
    result: list[MapPlayers] = []
    section_by_id: dict[str, Tag] = {}
    for g in stats_root.select(".vm-stats-game"):
        key_val = g.get("data-game-id")
        key = key_val if isinstance(key_val, str) else ""
        section_by_id[key] = g
    
    for gid_raw in ordered_ids:
        if limit is not None and len(result) >= limit:
            break
        game = section_by_id.get(gid_raw)
        if game is None:
            continue
        
        game_id_val = game.get("data-game-id")
        game_id = game_id_val if isinstance(game_id_val, str) else None
        gid: int | str | None = None
        
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
        teams_tuple: tuple[MapTeamScore, MapTeamScore] | None = None
        header = game.select_one(".vm-stats-game-header")
        if header:
            team_divs = header.select(".team")
            if len(team_divs) >= 2:
                # Team 1
                t1_name_el = team_divs[0].select_one(".team-name")
                t1_name = extract_text(t1_name_el) if t1_name_el else None
                t1_score_el = team_divs[0].select_one(".score")
                t1_score = parse_int(extract_text(t1_score_el)) if t1_score_el else None
                classes_val = t1_score_el.get("class") if t1_score_el else None
                score_classes1: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                t1_is_winner = "mod-win" in score_classes1 if t1_score_el else False
                
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
                classes_val2 = t2_score_el.get("class") if t2_score_el else None
                score_classes2: list[str] = [str(c) for c in classes_val2] if isinstance(classes_val2, (list, tuple)) else []
                t2_is_winner = "mod-win" in score_classes2 if t2_score_el else False
                
                # Parse attacker/defender rounds for team 2
                t2_ct = team_divs[1].select_one(".mod-ct")
                t2_t = team_divs[1].select_one(".mod-t")
                t2_ct_rounds = parse_int(extract_text(t2_ct)) if t2_ct else None
                t2_t_rounds = parse_int(extract_text(t2_t)) if t2_t else None
                
                if t1_name and t2_name:
                    c1 = canonical(t1_name)
                    c2 = canonical(t2_name)
                    t1_meta = team_meta_lookup.get(c1) if c1 else None
                    t2_meta = team_meta_lookup.get(c2) if c2 else None
                    
                    t1_id_val = t1_meta.get("id") if t1_meta else None
                    t1_short_val = t1_meta.get("short") if t1_meta else None
                    t2_id_val = t2_meta.get("id") if t2_meta else None
                    t2_short_val = t2_meta.get("short") if t2_meta else None
                    
                    teams_tuple = (
                        MapTeamScore(
                            id=t1_id_val if isinstance(t1_id_val, int) else None,
                            name=t1_name,
                            short=t1_short_val if isinstance(t1_short_val, str) else None,
                            score=t1_score,
                            attacker_rounds=t1_t_rounds,
                            defender_rounds=t1_ct_rounds,
                            is_winner=t1_is_winner,
                        ),
                        MapTeamScore(
                            id=t2_id_val if isinstance(t2_id_val, int) else None,
                            name=t2_name,
                            short=t2_short_val if isinstance(t2_short_val, str) else None,
                            score=t2_score,
                            attacker_rounds=t2_t_rounds,
                            defender_rounds=t2_ct_rounds,
                            is_winner=t2_is_winner,
                        ),
                    )
        
        # Parse rounds
        rounds_list: list[RoundResult] = []
        rounds_container = game.select_one(".vlr-rounds")
        if rounds_container:
            round_rows = rounds_container.select(".vlr-rounds-row")
            # Determine top/bottom team order from the rounds legend
            round_team_names: list[str] = []
            if round_rows:
                header_col = round_rows[0].select_one(".vlr-rounds-row-col")
                if header_col:
                    round_team_names = [extract_text(team_el) for team_el in header_col.select(".team")]
            # Flatten all round columns across rows, skipping headers/spacing
            flat_columns: list[Tag] = []
            for row in round_rows:
                for col in row.select(".vlr-rounds-row-col"):
                    if col.select_one(".team"):
                        continue
                    classes_val = col.get("class")
                    col_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                    if "mod-spacing" in col_classes:
                        continue
                    flat_columns.append(col)
            prev_score: tuple[int, int] | None = None
            final_score_tuple: tuple[int, int] | None = None
            if teams_tuple and all(ts.score is not None for ts in teams_tuple):
                final_score_tuple = (teams_tuple[0].score or 0, teams_tuple[1].score or 0)
            for col in flat_columns:
                rnd_num_el = col.select_one(".rnd-num")
                if not rnd_num_el:
                    continue
                rnd_num = parse_int(extract_text(rnd_num_el))
                if rnd_num is None:
                    continue
                title_val = col.get("title")
                title = (title_val if isinstance(title_val, str) else "").strip()
                if not title and not col.select_one(".rnd-sq.mod-win"):
                    # No data beyond this point
                    break
                score_tuple: tuple[int, int] | None = None
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
                    classes_val = winner_sq.get("class")
                    win_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                    if "mod-t" in win_classes:
                        winner_side = "Attacker"
                    elif "mod-ct" in win_classes:
                        winner_side = "Defender"
                    method_img = winner_sq.select_one("img")
                    if method_img:
                        src_val = method_img.get("src")
                        src = (src_val if isinstance(src_val, str) else "").lower()
                        if "elim" in src:
                            method = "Elimination"
                        elif "defuse" in src:
                            method = "SpikeDefused"
                        elif "boom" in src or "explosion" in src:
                            method = "SpikeExplosion"
                        elif "time" in src:
                            method = "TimeRunOut"
                winner_idx: int | None = None
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
                        canon_name = canonical(team_name)
                        winner_meta: dict[str, str | int | None] | None = team_meta_lookup.get(canon_name) if canon_name else None
                        if winner_meta:
                            _id = winner_meta.get("id")
                            _short = winner_meta.get("short")
                            _name = winner_meta.get("name")
                            winner_team_id = _id if isinstance(_id, int) else None
                            winner_team_short = _short if isinstance(_short, str) else None
                            winner_team_name = _name if isinstance(_name, str) else None
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
        def extract_mod_both(cell: Tag | None) -> str | None:
            if not cell:
                return None
            # Prefer spans containing mod-both
            for selector in [".side.mod-both", ".side.mod-side.mod-both", ".mod-both"]:
                el = cell.select_one(selector)
                if el:
                    return extract_text(el)
            for el in cell.select("span"):
                classes_val = el.get("class")
                classes: list[str] = list(classes_val) if isinstance(classes_val, (list, tuple)) else []
                if classes and any("mod-both" in cls for cls in classes):
                    return extract_text(el)
            return extract_text(cell)
        
        def parse_numeric(text: str | None) -> float | None:
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
        players: list[PlayerStats] = []
        tables = game.select("table.wf-table-inset")
        team_scores = list(teams_tuple) if teams_tuple else []
        for table_idx, table in enumerate(tables):
            tbody = table.select_one("tbody")
            if not tbody:
                continue
            team_score = team_scores[table_idx] if table_idx < len(team_scores) else None
            team_meta: dict[str, str | int | None] | None = None
            if team_score:
                canon_score_name = canonical(team_score.name)
                team_meta = team_meta_lookup.get(canon_score_name) if canon_score_name else None
            short_source = team_meta.get("short") if team_meta else (team_score.short if team_score else None)
            inferred_team_short = short_source if isinstance(short_source, str) else None
            inferred_team_id_val = team_meta.get("id") if team_meta else (team_score.id if team_score else None)
            inferred_team_id = inferred_team_id_val if isinstance(inferred_team_id_val, int) else None
            for row in tbody.select("tr"):
                player_cell = row.select_one(".mod-player")
                if not player_cell:
                    continue
                player_link = player_cell.select_one("a[href*='/player/']")
                if not player_link:
                    continue
                href_val = player_link.get("href")
                href = href_val if isinstance(href_val, str) else None
                player_id = extract_id_from_url(href, "player")
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
                    classes_val = flag.get("class")
                    player_flag_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                    for cls in player_flag_classes:
                        if cls.startswith("mod-") and cls != "mod-dark":
                            country_code = cls.removeprefix("mod-")
                            country = COUNTRY_MAP.get(country_code.upper(), country_code.upper())
                            break
                # Agents
                agents: list[str] = []
                agents_cell = row.select_one(".mod-agents")
                if agents_cell:
                    for img in agents_cell.select("img"):
                        title_val = img.get("title")
                        alt_val = img.get("alt")
                        agent_name = title_val if isinstance(title_val, str) else (alt_val if isinstance(alt_val, str) else "")
                        if agent_name:
                            agents.append(agent_name)
                # Stats
                stat_cells = row.select(".mod-stat")
                values: list[float | None] = [parse_numeric(extract_mod_both(cell)) for cell in stat_cells]
                def as_int(idx: int) -> int | None:
                    if idx >= len(values) or values[idx] is None:
                        return None
                    val = values[idx]
                    return int(val) if val is not None else None
                def as_float(idx: int) -> float | None:
                    if idx >= len(values) or values[idx] is None:
                        return None
                    return values[idx]
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
