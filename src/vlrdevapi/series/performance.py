"""Series performance functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import MapPerformance, KillMatrixEntry, PlayerPerformance
from ._parser import _WHITESPACE_RE, _MAP_NUMBER_RE
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, parse_int

_config = get_config()


def performance(series_id: int, limit: int | None = None, timeout: float | None = None) -> list[MapPerformance]:
    """
    Get performance statistics for a series.

    Args:
        series_id: Series/match ID
        limit: Maximum number of maps to return (optional)
        timeout: Request timeout in seconds

    Returns:
        List of map performance statistics

    Example:
        >>> import vlrdevapi as vlr
        >>> perf = vlr.series.performance(series_id=542210)
        >>> for game in perf:
        ...     print(f"Game: {game.map_name}")
        ...     for player in game.player_performances:
        ...         print(f"  {player.name}: {player.multi_2k} 2Ks, {player.econ} ECON")
    """
    url = f"{_config.vlr_base}/{series_id}?game=all&tab=performance"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []

    soup = BeautifulSoup(html, "lxml")
    stats_root = soup.select_one(".vm-stats")
    if not stats_root:
        return []

    # Extract team IDs from page header (similar to matches module)
    page_team_ids: list[int | None] = [None, None]
    page = soup  # Full page soup
    match_header = page.select_one(".wf-card.match-header")
    if match_header:
        from ..utils import extract_id_from_url
        t1_link = match_header.select_one(".match-header-link.mod-1")
        t2_link = match_header.select_one(".match-header-link.mod-2")
        if t1_link:
            href_val = t1_link.get("href")
            href = href_val if isinstance(href_val, str) else None
            page_team_ids[0] = extract_id_from_url(href, "team")
        if t2_link:
            href_val = t2_link.get("href")
            href = href_val if isinstance(href_val, str) else None
            page_team_ids[1] = extract_id_from_url(href, "team")

    # Get team tags from page to map to IDs
    team_tag_to_id: dict[str, int | None] = {}
    if match_header:
        # Get team names from the .wf-title-med elements
        team_title_els = match_header.select(".wf-title-med")
        if len(team_title_els) >= 2:
            team1_name = extract_text(team_title_els[0])
            team2_name = extract_text(team_title_els[1])
            if team1_name:
                team1_upper = team1_name.strip().upper()
                if page_team_ids[0]:
                    team_tag_to_id[team1_upper] = page_team_ids[0]

                # Handle common abbreviations
                if team1_upper == "TEAM LIQUID":
                    team_tag_to_id["TL"] = page_team_ids[0]
                elif team1_upper == "DRX":
                    team_tag_to_id["DRX"] = page_team_ids[0]  # DRX is both full name and abbreviation

            if team2_name:
                team2_upper = team2_name.strip().upper()
                if page_team_ids[1]:
                    team_tag_to_id[team2_upper] = page_team_ids[1]

                # Handle common abbreviations
                if team2_upper == "TEAM LIQUID":
                    team_tag_to_id["TL"] = page_team_ids[1]
                elif team2_upper == "DRX":
                    team_tag_to_id["DRX"] = page_team_ids[1]  # DRX is both full name and abbreviation

    # If team IDs weren't found from the header, fetch the main match page to get team IDs
    if not all(id is not None for id in page_team_ids):
        # Try to get the main match page (overview tab) to extract team IDs
        overview_url = f"{_config.vlr_base}/{series_id}"
        try:
            overview_html = fetch_html(overview_url, effective_timeout)
            overview_soup = BeautifulSoup(overview_html, "lxml")
            overview_match_header = overview_soup.select_one(".wf-card.match-header")
            if overview_match_header:
                t1_link = overview_match_header.select_one(".match-header-link.mod-1")
                t2_link = overview_match_header.select_one(".match-header-link.mod-2")
                if t1_link and page_team_ids[0] is None:
                    href_val = t1_link.get("href")
                    href = href_val if isinstance(href_val, str) else None
                    page_team_ids[0] = extract_id_from_url(href, "team")
                if t2_link and page_team_ids[1] is None:
                    href_val = t2_link.get("href")
                    href = href_val if isinstance(href_val, str) else None
                    page_team_ids[1] = extract_id_from_url(href, "team")

                # Also extract team names from the overview page
                team_title_els = overview_match_header.select(".wf-title-med")
                if len(team_title_els) >= 2:
                    team1_name = extract_text(team_title_els[0])
                    team2_name = extract_text(team_title_els[1])
                    if team1_name:
                        team1_upper = team1_name.strip().upper()
                        if page_team_ids[0]:
                            team_tag_to_id[team1_upper] = page_team_ids[0]

                        # Handle common abbreviations
                        if team1_upper == "TEAM LIQUID":
                            team_tag_to_id["TL"] = page_team_ids[0]
                        elif team1_upper == "DRX":
                            team_tag_to_id["DRX"] = page_team_ids[0]  # DRX is both full name and abbreviation

                    if team2_name:
                        team2_upper = team2_name.strip().upper()
                        if page_team_ids[1]:
                            team_tag_to_id[team2_upper] = page_team_ids[1]

                        # Handle common abbreviations
                        if team2_upper == "TEAM LIQUID":
                            team_tag_to_id["TL"] = page_team_ids[1]
                        elif team2_upper == "DRX":
                            team_tag_to_id["DRX"] = page_team_ids[1]  # DRX is both full name and abbreviation
        except NetworkError:
            # If we can't fetch the overview page, continue with what we have
            pass

    # Add additional common team abbreviations that might be used in performance tables
    # Create reverse mapping based on known full team names in the dictionary
    common_abbreviations = {
        "TL": "TEAM LIQUID",
        "DRX": "DRX",
        "FNC": "FNC ESPORTS",
        "G2": "G2",
        "ENCE": "ENCE",
        "LOUD": "LOUD",
        "PRX": "PAPER REX",
        "T1": "T1",
        "GEN": "GEN.G",
        "LEV": "LEVIATAN",
        "KRÜ": "KRÜ ESPORTS",
        "KPR": "KATARU",
        "ZETA": "ZETA DIVISION",
        "TF": "TWO ALPHA",
        "FUT": "FUTURO",
        "KC": "KEYD STARS",
        "INF": "INFINITE ESPORTS",
        "GX": "GIANTX",
        "NRG": "NRG",
        "SEN": "SENPAI ESPORTS",
        "ACN": "AVANTARIA CINCO",
        "KBM": "KBM PLUG'N PLAY",
        "FUR": "FURIA ESPORTS",
        "BAD": "BAD NEWS EAGLES",
        "C9": "CLOUD9",
        "EG": "EVIL GENIUSES",
        "OPTC": "OPTC",
        "TSM": "TSM",
        "100T": "100 THIEVES",
        "FNC": "FNC ESPORTS",
        "BBL": "BIGBEN LOUNGE",
        "GIA": "GIANTX",
        "RENA": "RENASCENCE",
        "VIT": "VITALITY",
        "GL": "GOLDEN GORILLAS",
    }

    # Map abbreviations to IDs based on what we already know
    for abbrev, full_name in common_abbreviations.items():
        full_upper = full_name.upper()
        if full_upper in team_tag_to_id and abbrev not in team_tag_to_id:
            team_tag_to_id[abbrev] = team_tag_to_id[full_upper]
    
    # Build game_id -> map name from tabs (including "All")
    game_name_map: dict[int | str, str] = {}
    for nav in stats_root.select("[data-game-id]"):
        classes_val = nav.get("class")
        nav_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
        # Skip the actual game sections (with exact class "vm-stats-game"), not the nav items
        if "vm-stats-game" in nav_classes:
            continue
        
        gid_val = nav.get("data-game-id")
        gid_str = gid_val if isinstance(gid_val, str) else None
        if not gid_str:
            continue
        
        txt = nav.get_text(" ", strip=True)
        if not txt:
            continue
        name = _MAP_NUMBER_RE.sub("", txt).strip()
        
        # Handle both "all" and numeric IDs
        if gid_str == "all":
            game_name_map["all"] = "All Maps"
        elif gid_str.isdigit():
            game_name_map[int(gid_str)] = name
    
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
    
    result: list[MapPerformance] = []
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
            map_name = game_name_map.get("all", "All Maps")
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
        
        # Parse kill matrices
        kill_matrix = _parse_kill_matrix(game, "mod-normal", team_tag_to_id)
        fkfd_matrix = _parse_kill_matrix(game, "mod-fkfd", team_tag_to_id)
        op_matrix = _parse_kill_matrix(game, "mod-op", team_tag_to_id)
        
        # Parse player performances from advanced stats table
        player_performances = _parse_player_performances(game, team_tag_to_id)
        
        # Skip maps with no data (unplayed maps)
        has_data = (
            len(kill_matrix) > 0 or 
            len(fkfd_matrix) > 0 or 
            len(op_matrix) > 0 or 
            len(player_performances) > 0
        )
        
        if not has_data:
            continue
        
        result.append(MapPerformance(
            game_id=gid,
            map_name=map_name,
            kill_matrix=kill_matrix,
            fkfd_matrix=fkfd_matrix,
            op_matrix=op_matrix,
            player_performances=player_performances,
        ))
    
    return result


def _parse_kill_matrix(game: Tag, matrix_class: str, team_tag_to_id: dict[str, int | None]) -> list[KillMatrixEntry]:
    """Parse a kill matrix table (normal, fkfd, or op)."""
    entries: list[KillMatrixEntry] = []

    # Find the table with the specified class
    table = game.select_one(f"table.wf-table-inset.mod-matrix.{matrix_class}")
    if not table:
        return entries

    # Try tbody first, fall back to table directly
    tbody = table.select_one("tbody")
    container = tbody if tbody else table

    rows = container.select("tr")
    if not rows:
        return entries

    # First row contains victim headers
    header_row = rows[0]
    victim_cells = header_row.select("td")[1:]  # Skip first empty cell
    victims: list[tuple[str, str | None, int | None]] = []  # (name, team_short, team_id)

    for cell in victim_cells:
        team_div = cell.select_one(".team")
        if team_div:
            # Extract player name
            name_div = team_div.select_one("div")
            if name_div:
                # The player name is in the first text node
                name_text = name_div.find(string=True, recursive=False)
                name = (name_text or "").strip() if name_text else None
                # Team tag is in the .team-tag element
                team_tag_el = name_div.select_one(".team-tag")
                team_tag = extract_text(team_tag_el) if team_tag_el else None
                # Get team ID from tag
                team_id = team_tag_to_id.get(team_tag.upper()) if team_tag else None
                if name:
                    victims.append((name, team_tag, team_id))

    # Remaining rows contain killer data
    for row in rows[1:]:
        cells = row.select("td")
        if not cells:
            continue

        # First cell is the killer
        killer_cell = cells[0]
        killer_team_div = killer_cell.select_one(".team")
        if not killer_team_div:
            continue

        killer_name_div = killer_team_div.select_one("div")
        if not killer_name_div:
            continue

        killer_name_text = killer_name_div.find(string=True, recursive=False)
        killer_name = (killer_name_text or "").strip() if killer_name_text else None
        killer_team_tag_el = killer_name_div.select_one(".team-tag")
        killer_team_tag = extract_text(killer_team_tag_el) if killer_team_tag_el else None
        killer_team_id = team_tag_to_id.get(killer_team_tag.upper()) if killer_team_tag else None

        if not killer_name:
            continue

        # Remaining cells are stats against each victim
        stat_cells = cells[1:]
        for i, stat_cell in enumerate(stat_cells):
            if i >= len(victims):
                break

            victim_name, victim_team, victim_team_id = victims[i]

            # Parse the stats: three divs for kills, deaths, differential
            stat_divs = stat_cell.select(".stats-sq")
            if len(stat_divs) >= 3:
                kills_text = extract_text(stat_divs[0])
                deaths_text = extract_text(stat_divs[1])
                diff_text = extract_text(stat_divs[2])

                kills = parse_int(kills_text)
                deaths = parse_int(deaths_text)
                differential = parse_int(diff_text)

                # Only add entry if there's actual data
                if kills is not None or deaths is not None:
                    # If victim team ID is still None, try to populate it from the killer's team info
                    # The table is structured so that players from the same team appear together
                    # Let's try to use a fallback method where if team IDs are missing,
                    # we assign them based on the team tags found in the table
                    final_killer_team_id = killer_team_id
                    final_victim_team_id = victim_team_id

                    # If we still don't have team IDs, try to determine them from the team tags
                    # by checking if the tag exists in our mapping or trying to find other entries
                    if not final_killer_team_id and killer_team_tag and killer_team_tag in team_tag_to_id:
                        final_killer_team_id = team_tag_to_id[killer_team_tag]
                    if not final_victim_team_id and victim_team and victim_team in team_tag_to_id:
                        final_victim_team_id = team_tag_to_id[victim_team]

                    entries.append(KillMatrixEntry(
                        killer_name=killer_name,
                        victim_name=victim_name,
                        killer_team_short=killer_team_tag,
                        killer_team_id=final_killer_team_id,
                        victim_team_short=victim_team,
                        victim_team_id=final_victim_team_id,
                        kills=kills,
                        deaths=deaths,
                        differential=differential,
                    ))

    return entries


def _parse_player_performances(game: Tag, team_tag_to_id: dict[str, int | None]) -> list[PlayerPerformance]:
    """Parse player performance stats from the performance stats table."""
    performances: list[PlayerPerformance] = []

    # Look for tables using multiple strategies to ensure we find the right one
    table = None

    # Strategy 1: Look for table with performance notable elements (most specific)
    for selector in [
        "table.wf-table-inset",
        "table",
        ".vm-stats-game table"  # Limit search to game sections
    ]:
        tables = game.select(selector)
        for t in tables:
            # Check if this table contains performance notable elements (indicates detailed stats)
            if t.select(".vm-perf-notable"):
                table = t
                break
        if table:
            break

    # Strategy 2: If not found, look for tables with both team elements and popable elements
    if not table:
        all_tables = game.select("table")
        for t in all_tables:
            if t.select_one(".team") and t.select(".wf-popable"):
                table = t
                break

    # Strategy 3: Look for tables that have the exact structure from the HTML
    if not table:
        # Look for tables that have stat squares with popable/perf-notable elements
        all_tables = game.select("table")
        for t in all_tables:
            # Check if table has both team elements (for player names) and performance notables
            if (t.select_one(".team") and
                (t.select(".vm-perf-notable") or t.select(".wf-popable") or
                 any("mod-d" in (elem.get("class") or []) for elem in t.select(".stats-sq")))):
                table = t
                break

    # Strategy 4: Last resort - find any table with team elements and sufficient columns
    if not table:
        all_tables = game.select("table")
        for t in all_tables:
            # Look for any row in the table with team in first cell and enough stat cells
            rows = t.select("tr")
            for row in rows:
                cells = row.select("td")
                if len(cells) >= 7 and cells[0].select_one(".team"):
                    table = t
                    break
            if table:
                break

    if not table:
        return performances

    # Try tbody first, fall back to table directly
    tbody = table.select_one("tbody")
    container = tbody if tbody else table

    rows = container.select("tr")
    # Skip header row
    data_rows = [r for r in rows if not r.select_one("th")]

    for row in data_rows:
        cells = row.select("td")
        # Check if we have minimum required cells
        if len(cells) < 7:
            continue

        # Cell 0: Player info
        player_cell = cells[0]
        team_div = player_cell.select_one(".team")
        if not team_div:
            continue

        div = team_div.select_one("div")
        if not div:
            continue

        # Player name is the first text node
        name_text = div.find(string=True, recursive=False)
        name = (name_text or "").strip() if name_text else None
        if not name:
            continue

        # Team tag
        team_tag_el = div.select_one(".team-tag")
        team_short = extract_text(team_tag_el) if team_tag_el else None
        team_id = team_tag_to_id.get(team_short.upper()) if team_short else None

        # Cell 1: Agent
        agent_cell = cells[1]
        agent_img = agent_cell.select_one("img")
        agent = None
        if agent_img:
            src_val = agent_img.get("src")
            src = src_val if isinstance(src_val, str) else ""
            # Extract agent name from path like "/img/vlr/game/agents/vyse.png"
            if src:
                parts = src.split("/")
                if parts:
                    filename = parts[-1]
                    agent = filename.replace(".png", "").capitalize()

        # Parse all available stats based on actual column positions
        # From the HTML you showed: 2K at position 2, 1v2 at position 7, etc.
        multi_2k, multi_2k_details = _parse_detailed_stat_cell(cells[2]) if len(cells) > 2 else (None, None)
        multi_3k, multi_3k_details = _parse_detailed_stat_cell(cells[3]) if len(cells) > 3 else (None, None)
        multi_4k, multi_4k_details = _parse_detailed_stat_cell(cells[4]) if len(cells) > 4 else (None, None)
        multi_5k, multi_5k_details = _parse_detailed_stat_cell(cells[5]) if len(cells) > 5 else (None, None)

        clutch_1v1, clutch_1v1_details = _parse_detailed_stat_cell(cells[6]) if len(cells) > 6 else (None, None)
        clutch_1v2, clutch_1v2_details = _parse_detailed_stat_cell(cells[7]) if len(cells) > 7 else (None, None)
        clutch_1v3, clutch_1v3_details = _parse_detailed_stat_cell(cells[8]) if len(cells) > 8 else (None, None)
        clutch_1v4, clutch_1v4_details = _parse_detailed_stat_cell(cells[9]) if len(cells) > 9 else (None, None)
        clutch_1v5, clutch_1v5_details = _parse_detailed_stat_cell(cells[10]) if len(cells) > 10 else (None, None)

        econ = _parse_stat_cell(cells[11]) if len(cells) > 11 else None
        plants = _parse_stat_cell(cells[12]) if len(cells) > 12 else None
        defuses = _parse_stat_cell(cells[13]) if len(cells) > 13 else None

        performances.append(PlayerPerformance(
            name=name,
            team_short=team_short,
            team_id=team_id,
            agent=agent,
            multi_2k=multi_2k,
            multi_3k=multi_3k,
            multi_4k=multi_4k,
            multi_5k=multi_5k,
            clutch_1v1=clutch_1v1,
            clutch_1v2=clutch_1v2,
            clutch_1v3=clutch_1v3,
            clutch_1v4=clutch_1v4,
            clutch_1v5=clutch_1v5,
            econ=econ,
            plants=plants,
            defuses=defuses,
            multi_2k_details=multi_2k_details,
            multi_3k_details=multi_3k_details,
            multi_4k_details=multi_4k_details,
            multi_5k_details=multi_5k_details,
            clutch_1v1_details=clutch_1v1_details,
            clutch_1v2_details=clutch_1v2_details,
            clutch_1v3_details=clutch_1v3_details,
            clutch_1v4_details=clutch_1v4_details,
            clutch_1v5_details=clutch_1v5_details,
        ))

    return performances


def _parse_detailed_stat_cell(cell: Tag):
    """Parse a stat value and detailed information from a cell with popable contents."""
    stat_sq = cell.select_one(".stats-sq")
    if not stat_sq:
        return None, None

    # Extract the numerical value, handling whitespace properly
    count = None
    # Get the direct text content of the stats-sq element (excluding content from child elements)
    # The number is the direct text content in the element
    direct_text = None

    # Method 1: Try to get direct text node content (text not in child elements)
    direct_children = []
    for content in stat_sq.contents:
        if content.name is None:  # This is a text node (not an HTML element)
            text_content = str(content).strip()
            if text_content:
                direct_children.append(text_content)

    if direct_children:
        # Take the first direct text content as the count
        text_to_parse = direct_children[0]
        count = parse_int(text_to_parse)
    else:
        # Method 2: If no direct text nodes, get direct text only (not from children)
        # Loop through the direct children of the element to find text nodes
        direct_text_content = ""
        for child in stat_sq.children:
            if isinstance(child, str) or (hasattr(child, 'strip') and child.name is None):
                # This is a text node (not an element)
                text_content = str(child).strip()
                if text_content:
                    direct_text_content = text_content
                    break  # Take the first direct text content

        if direct_text_content:
            count = parse_int(direct_text_content)

    # If both methods failed, fall back to extract_text
    if count is None:
        text = extract_text(stat_sq).strip()
        if text:
            # Take only the first part if there are multiple values
            first_part = text.split()[0] if text.split() else text
            count = parse_int(first_part)

    # Extract detailed information from popable contents if present
    details = []

    popable_contents = stat_sq.select_one(".wf-popable-contents")

    if popable_contents:
        # A single popable content might have multiple round entries
        # Each round entry has a 'white-space: nowrap' div with the round number,
        # followed by player elements

        # Look for all round elements (there may be multiple if the player had multiple multikills in different rounds)
        round_divs = popable_contents.select("div[style*='white-space: nowrap']")

        for round_div in round_divs:
            # Get the round number for this specific event
            round_span = round_div.select_one("span")
            round_number = None
            if round_span:
                round_text = extract_text(round_span)
                round_number = parse_int(round_text)

            # Find the player elements that follow this specific round div
            # We need to look for players that are related to this specific round
            # The players are usually in the divs within the same container that follow the round div
            players_killed = []

            # Get all player elements in the same container as this round div
            container = round_div.parent if round_div.parent else None
            if container:
                # Find all player elements in this container
                all_player_elements = container.select("div[style*='display: flex; align-items: center']")

                for player_elem in all_player_elements:
                    player_text = extract_text(player_elem).strip()
                    if player_text:
                        # Extract just the player name (after the agent name/image)
                        parts = player_text.split()
                        # The player name is usually the last part after the image tag
                        # Example: "omen keiko" -> "keiko", "neon kamo" -> "kamo"
                        if len(parts) >= 2:
                            # Take the last part as the player name
                            player_name = parts[-1]
                            players_killed.append(player_name)
                        elif len(parts) == 1:
                            # If only one part, use it as player name
                            players_killed.append(parts[0])
                        else:
                            # If it's blank for some reason, skip
                            continue

                # Create a detail entry for this specific round if we have both round and players
                if round_number is not None and players_killed:
                    # Determine if this is a multi-kill or clutch based on the class modifiers
                    classes = stat_sq.get("class", [])
                    is_multikill = any(mod in classes for mod in ["mod-d", "mod-c", "mod-b", "mod-a"])
                    is_clutch = any(mod in classes for mod in ["mod-e", "mod-f", "mod-g", "mod-h", "mod-i"])

                    from .models import MultiKillDetail, ClutchDetail
                    if is_multikill:
                        details.append(MultiKillDetail(round_number=round_number, players_killed=players_killed))
                    elif is_clutch:
                        details.append(ClutchDetail(round_number=round_number, players_killed=players_killed))

    return count, details if details else None


def _parse_stat_cell(cell: Tag) -> int | None:
    """Parse a stat value from a cell."""
    stat_sq = cell.select_one(".stats-sq")
    if not stat_sq:
        return None
    text = extract_text(stat_sq)
    return parse_int(text)
