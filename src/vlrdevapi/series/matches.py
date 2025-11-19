"""Series matches functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import MapPlayers, PlayerStats, MapTeamScore, RoundResult
from ._parser import _WHITESPACE_RE, _MAP_NUMBER_RE
from .info import info
from ..config import get_config
from ..countries import COUNTRY_MAP
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, parse_int, extract_id_from_url

_config = get_config()


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
        # Skip "all" if there's only one match (it would be redundant)
        include_all = has_all and len(numeric_ids) > 1
        ordered_ids = (["all"] if include_all else []) + [g for _, g in numeric_ids]
    
    if not ordered_ids:
        ordered_ids = []
        for g in stats_root.select(".vm-stats-game"):
            val = g.get("data-game-id")
            s = val if isinstance(val, str) else None
            ordered_ids.append(s or "")

    # Filter out "all" if there is only one actual match
    numeric_count = sum(1 for x in ordered_ids if x != "all" and x.isdigit())
    if numeric_count <= 1 and "all" in ordered_ids:
        ordered_ids = [x for x in ordered_ids if x != "all"]
    
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
