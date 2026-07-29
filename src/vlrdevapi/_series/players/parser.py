
import re

from selectolax.parser import HTMLParser, Node

from vlrdevapi._series.players.models import (
    PlayerGameStats,
    PlayersStats,
    PlayerStats,
    SideStats,
    TeamPlayers,
)
from vlrdevapi.commons.countries import get_country_name
import contextlib


def _parse_pct(val: str) -> float | None:
    """Parse a percentage string into a float.

    Args:
        val: Percentage string (e.g., '75%').

    Returns:
        float | None: Decimal value (e.g., 0.75), or None on failure.

    """
    val = val.strip().rstrip("%")
    try:
        return float(val) / 100.0
    except ValueError:
        return None


def _parse_int(val: str) -> int | None:
    """Parse an integer string, stripping leading '+' sign.

    Args:
        val: Integer string (e.g., '5' or '+3').

    Returns:
        int | None: Parsed integer, or None on failure.

    """
    val = val.strip().lstrip("+")
    try:
        return int(val)
    except ValueError:
        return None


def _parse_float(val: str) -> float | None:
    """Parse a float string.

    Args:
        val: Float string (e.g., '1.5').

    Returns:
        float | None: Parsed value, or None on failure.

    """
    try:
        return float(val.strip())
    except ValueError:
        return None


def _get_side_value(td: Node, css_class: str, parse_fn) -> float | None:
    """Extract and parse a span value from a table cell by CSS class.

    Args:
        td: The table cell Node.
        css_class: CSS class of the target span (e.g., 'mod-both').
        parse_fn: Parsing function (_parse_int, _parse_float, or
            _parse_pct).

    Returns:
        float | None: Parsed numeric value, or None if not found.

    """
    el = td.css_first(f"span.{css_class}")
    if el:
        return parse_fn(el.text(strip=True))
    return None


def _parse_side_stats(td_overall, td_attack, td_defend, is_pct: bool = False) -> tuple:
    """Parse overall/attack/defend stat cells into a tuple of values.

    Args:
        td_overall: Table cell for combined stats.
        td_attack: Table cell for attack-side stats.
        td_defend: Table cell for defense-side stats.
        is_pct: Whether the stat is a percentage value.

    Returns:
        tuple: (overall_value, attack_value, defend_value).

    """
    if is_pct:
        fn = _parse_pct
    elif any(
        c in (td_overall.attributes.get("class") or "")
        for c in ("mod-kd-diff", "mod-fk-diff")
    ):
        fn = _parse_int
    else:
        fn = _parse_float

    overall = _get_side_value(td_overall, "mod-both", fn)
    attack = _get_side_value(td_attack, "mod-t", fn)
    defend = _get_side_value(td_defend, "mod-ct", fn)
    return overall, attack, defend


def _parse_stat_cell(td: Node) -> tuple:
    """Parse a single stat cell for overall, attack, and defend values.

    Args:
        td: The table cell Node.

    Returns:
        tuple: (overall_value, attack_value, defend_value).

    """
    is_pct = "%" in (td.text(strip=True) if td else "")
    cls = td.attributes.get("class", "") or ""

    if is_pct:
        fn = _parse_pct
    elif "mod-kd-diff" in cls or "mod-fk-diff" in cls:
        fn = _parse_int
    else:
        fn = _parse_float

    overall = _get_side_value(td, "mod-both", fn)
    attack = _get_side_value(td, "mod-t", fn)
    defend = _get_side_value(td, "mod-ct", fn)
    return overall, attack, defend


def _parse_player_row(cell: Node) -> PlayerGameStats:
    player = PlayerGameStats()

    a = cell.css_first("a")
    if a:
        href = a.attributes.get("href", "") or ""
        parts = href.strip("/").split("/")
        if len(parts) >= 2:
            with contextlib.suppress(ValueError):
                player.player_id = int(parts[1])

    name_el = cell.css_first(".ovw-player-name")
    if name_el:
        player.name = name_el.text(strip=True)
    else:
        bold_el = cell.css_first("div[style*='font-weight: 700']")
        if bold_el:
            player.name = bold_el.text(strip=True)
        else:
            for div in cell.css("div"):
                text = div.text(strip=True)
                if text and len(text) <= 20 and not div.css("div"):
                    player.name = text
                    break

    team_el = cell.css_first(".ovw-player-tag")
    if team_el:
        player.team_short = team_el.text(strip=True)

    flag_el = cell.css_first("i.flag")
    if flag_el:
        for cls in (flag_el.attributes.get("class") or "").split():
            if cls.startswith("mod-") and cls != "mod-none":
                player.country_code = cls[4:]
                player.country = get_country_name(player.country_code)
                break

    for img in cell.css(".ovw-agents img"):
        alt = img.attributes.get("alt", "") or ""
        if alt:
            player.agents.append(alt.title())

    return player


def _parse_kda_cell(cell: Node) -> tuple:
    kills_o = kills_a = kills_d = None
    deaths_o = deaths_a = deaths_d = None
    assists_o = assists_a = assists_d = None

    for stat_span in cell.css("span.ovw-kda-stat"):
        col = stat_span.attributes.get("data-col", "")
        both_el = stat_span.css_first("span.mod-both")
        t_el = stat_span.css_first("span.mod-t")
        ct_el = stat_span.css_first("span.mod-ct")
        both = _parse_int(both_el.text(strip=True)) if both_el is not None else None
        t = _parse_int(t_el.text(strip=True)) if t_el is not None else None
        ct = _parse_int(ct_el.text(strip=True)) if ct_el is not None else None
        if col == "kills":
            kills_o, kills_a, kills_d = both, t, ct
        elif col == "deaths":
            deaths_o, deaths_a, deaths_d = both, t, ct
        elif col == "assists":
            assists_o, assists_a, assists_d = both, t, ct

    return (kills_o, kills_a, kills_d, deaths_o, deaths_a, deaths_d, assists_o, assists_a, assists_d)


def _parse_table(table: Node) -> list[PlayerGameStats]:
    players: list[PlayerGameStats] = []
    rows = table.css("div.ovw-row")
    for row in rows:
        cls = row.attributes.get("class", "") or ""
        if "mod-head" in cls:
            continue

        cells = row.css("div.ovw-cell")
        if len(cells) < 11:
            continue

        player = _parse_player_row(cells[0])

        rating_vals = _parse_stat_cell(cells[1])
        acs_vals = _parse_stat_cell(cells[2])
        kills_vals, deaths_vals, assists_vals = None, None, None
        kda_vals = _parse_kda_cell(cells[3])
        kills_vals = (kda_vals[0], kda_vals[1], kda_vals[2])
        deaths_vals = (kda_vals[3], kda_vals[4], kda_vals[5])
        assists_vals = (kda_vals[6], kda_vals[7], kda_vals[8])
        kd_diff_vals = _parse_stat_cell(cells[4])
        kast_vals = _parse_stat_cell(cells[5])
        adr_vals = _parse_stat_cell(cells[6])
        hs_percent_vals = _parse_stat_cell(cells[7])
        first_kills_vals = _parse_stat_cell(cells[8])
        first_deaths_vals = _parse_stat_cell(cells[9])
        fk_fd_diff_vals = _parse_stat_cell(cells[10])

        def _build_side(
            rating_t, acs_t, kills_t, deaths_t, assists_t, kd_diff_t, kast_t, adr_t, hs_percent_t, first_kills_t, first_deaths_t, fk_fd_diff_t,
        ) -> SideStats:
            return SideStats(
                rating=rating_t,
                acs=acs_t,
                kills=kills_t,
                deaths=deaths_t,
                assists=assists_t,
                kd_diff=kd_diff_t,
                kast=kast_t,
                adr=adr_t,
                hs_percent=hs_percent_t,
                first_kills=first_kills_t,
                first_deaths=first_deaths_t,
                fk_fd_diff=fk_fd_diff_t,
            )

        player.stats = PlayerStats(
            overall=_build_side(
                rating_vals[0], acs_vals[0], kills_vals[0], deaths_vals[0], assists_vals[0],
                kd_diff_vals[0], kast_vals[0], adr_vals[0], hs_percent_vals[0],
                first_kills_vals[0], first_deaths_vals[0], fk_fd_diff_vals[0],
            ),
            attack=_build_side(
                rating_vals[1], acs_vals[1], kills_vals[1], deaths_vals[1], assists_vals[1],
                kd_diff_vals[1], kast_vals[1], adr_vals[1], hs_percent_vals[1],
                first_kills_vals[1], first_deaths_vals[1], fk_fd_diff_vals[1],
            ),
            defend=_build_side(
                rating_vals[2], acs_vals[2], kills_vals[2], deaths_vals[2], assists_vals[2],
                kd_diff_vals[2], kast_vals[2], adr_vals[2], hs_percent_vals[2],
                first_kills_vals[2], first_deaths_vals[2], fk_fd_diff_vals[2],
            ),
        )

        players.append(player)

    return players


def _parse_team_link(el: Node | None) -> tuple[int, str]:
    """Parse a team link element for team ID and name.

    Args:
        el: The team link Node, or None.

    Returns:
        tuple[int, str]: (team_id, team_name).

    """
    team_id = 0
    team_name = ""
    if not el:
        return team_id, team_name

    href = el.attributes.get("href", "") or ""
    parts = href.strip("/").split("/")
    if len(parts) >= 2:
        with contextlib.suppress(ValueError):
            team_id = int(parts[1])

    name_el = el.css_first(".wf-title-med")
    if name_el:
        team_name = name_el.text(strip=True)

    return team_id, team_name


def parse_players_stats(html: HTMLParser, game_id: str = "all") -> PlayersStats:
    """Parse player statistics from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.
        game_id: Game/map identifier ('all' for combined, or numeric ID).

    Returns:
        PlayersStats: Parsed player stats for both teams.

    """
    result = PlayersStats()

    link1 = html.css_first(".match-header-link.mod-1")
    link2 = html.css_first(".match-header-link.mod-2")
    team1_id, team1_name = _parse_team_link(link1)
    team2_id, team2_name = _parse_team_link(link2)

    game_div = html.css_first(f'.vm-stats-game[data-game-id="{game_id}"]')
    if not game_div:
        return result

    if game_id != "all":
        map_div = game_div.css_first(".vm-stats-game-header .map")
        if map_div:
            bold_div = map_div.css_first("div[style*='font-weight: 700']")
            if bold_div:
                m = re.search(r"<span[^>]*>\s*([A-Za-z]+)", bold_div.html or "")
                if m:
                    result.map_name = m.group(1)
            if not result.map_name:
                result.map_name = map_div.text(strip=True)

    tables = game_div.css("div.ovw-table")
    if len(tables) < 2:
        return result

    team1_players = _parse_table(tables[0])
    team2_players = _parse_table(tables[1])

    team1_short = team1_players[0].team_short if team1_players else ""
    team2_short = team2_players[0].team_short if team2_players else ""

    result.team1 = TeamPlayers(
        team_id=team1_id,
        team_name=team1_name,
        team_short=team1_short,
        players=team1_players,
    )
    result.team2 = TeamPlayers(
        team_id=team2_id,
        team_name=team2_name,
        team_short=team2_short,
        players=team2_players,
    )

    return result
