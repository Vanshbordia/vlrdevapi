
from selectolax.parser import HTMLParser, Node

from vlrdevapi._series.performance.models import (
    AdvStatsEntry,
    AdvStatsNotableRound,
    KillEntry,
    KillMatrix,
    NotableVictim,
    PerformanceData,
)
import contextlib


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


def _parse_player_from_td(td: Node) -> tuple[str, int, str]:
    """Parse player name, ID, and team abbreviation from a table cell.

    Args:
        td: The table cell Node containing player info.

    Returns:
        tuple[str, int, str]: (player_name, player_id, team_short).

    """
    name = ""
    player_id = 0
    team_short = ""

    a = td.css_first("a")
    if a:
        href = a.attributes.get("href", "") or ""
        parts = href.strip("/").split("/")
        if len(parts) >= 2:
            with contextlib.suppress(ValueError):
                player_id = int(parts[1])

    team_tag = td.css_first(".team-tag")
    if team_tag:
        team_short = team_tag.text(strip=True)
        parent = team_tag.parent
        if parent and parent.tag == "div":
            name = parent.text(deep=False, strip=True)

    return name, player_id, team_short


def _parse_matrix_cell(td: Node) -> tuple[int | None, int | None, int | None, bool]:
    """Parse a kill matrix cell for kills, deaths, and diff.

    Args:
        td: The table cell Node.

    Returns:
        tuple[int | None, int | None, int | None, bool]: (kills, deaths, diff, is_null).

    """
    flex_div = td.css_first('div[style*="display: flex"]')
    if not flex_div:
        sq_divs = td.css("div.stats-sq")
        if sq_divs:
            val = sq_divs[0].text(deep=False, strip=True)
            return _parse_int(val), None, None, False
        return None, None, None, True

    sq_divs = flex_div.css("div.stats-sq")
    if len(sq_divs) < 3:
        return None, None, None, True

    kills_text = sq_divs[0].text(deep=False, strip=True)
    deaths_text = sq_divs[1].text(deep=False, strip=True)
    diff_text = sq_divs[2].text(deep=False, strip=True)

    if not kills_text and not deaths_text:
        return None, None, None, True

    return _parse_int(kills_text), _parse_int(deaths_text), _parse_int(diff_text), False


def _parse_matrix_table(table: Node) -> KillMatrix:
    """Parse a kill matrix table into a KillMatrix model.

    Args:
        table: The table Node containing the kill matrix.

    Returns:
        KillMatrix: Parsed kill entries with killer/victim pairs.

    """
    matrix = KillMatrix()
    rows = table.css("tr")
    if not rows:
        return matrix

    header_row = rows[0]
    header_tds = header_row.css("td")
    col_players = [_parse_player_from_td(td) for td in header_tds[1:]]

    for row in rows[1:]:
        tds = row.css("td")
        if not tds:
            continue

        killer_name, killer_id, killer_team = _parse_player_from_td(tds[0])

        for j, td in enumerate(tds[1:]):
            if j >= len(col_players):
                break
            victim_name, victim_id, victim_team = col_players[j]
            kills, deaths, diff, is_null = _parse_matrix_cell(td)

            matrix.entries.append(
                KillEntry(
                    killer=killer_name,
                    killer_id=killer_id,
                    killer_team=killer_team,
                    victim=victim_name,
                    victim_id=victim_id,
                    victim_team=victim_team,
                    kills=kills,
                    deaths=deaths,
                    diff=diff,
                ),
            )

    return matrix


def _parse_notable_rounds(
    popable_div: Node | None, player_mapping: dict[str, int],
) -> list[AdvStatsNotableRound]:
    """Parse notable round details from a popover div.

    Args:
        popable_div: The popover content Node, or None.
        player_mapping: Mapping of player names to player IDs.

    Returns:
        list[AdvStatsNotableRound]: Parsed notable round entries.

    """
    rounds: list[AdvStatsNotableRound] = []
    if not popable_div:
        return rounds

    round_divs = popable_div.css('div[style*="margin-top: 10px"]')
    for rd in round_divs:
        round_span = rd.css_first("span")
        if not round_span:
            continue
        round_num = _parse_int(round_span.text(strip=True))

        victims: list[NotableVictim] = []
        victim_divs = rd.css('div[style*="align-items: center"]')
        for vd in victim_divs:
            text = vd.text(strip=True)
            if text:
                player_id = player_mapping.get(text)
                victims.append(NotableVictim(name=text, player_id=player_id))

        rounds.append(AdvStatsNotableRound(round_number=round_num, victims=victims))

    return rounds


def _parse_adv_stats_row(tr: Node, player_mapping: dict[str, int]) -> AdvStatsEntry:
    """Parse an advanced stats row into an AdvStatsEntry.

    Args:
        tr: The table row Node.
        player_mapping: Mapping of player names to player IDs.

    Returns:
        AdvStatsEntry: Parsed advanced stats entry.

    """
    entry = AdvStatsEntry()
    tds = tr.css("td")
    if len(tds) < 14:
        return entry

    player_td = tds[0]
    name, player_id, team_short = _parse_player_from_td(player_td)
    entry.name = name
    entry.player_id = player_id
    entry.team_short = team_short

    agent_td = tds[1]
    agent_img = agent_td.css_first("img")
    if agent_img:
        src = agent_img.attributes.get("src", "") or ""
        agent_name = src.rsplit("/", 1)[-1].replace(".png", "")
        entry.agent = agent_name.title()

    stat_fields = [
        ("two_k", "mod-d", "two_k_rounds"),
        ("three_k", "mod-c", "three_k_rounds"),
        ("four_k", "mod-b", "four_k_rounds"),
        ("five_k", None, "five_k_rounds"),
        ("one_v1", "mod-e", "one_v1_rounds"),
        ("one_v2", None, "one_v2_rounds"),
        ("one_v3", None, "one_v3_rounds"),
        ("one_v4", None, "one_v4_rounds"),
        ("one_v5", None, "one_v5_rounds"),
    ]

    stat_tds = tds[2:11]
    for i, (field_name, notable_cls, rounds_field) in enumerate(stat_fields):
        if i >= len(stat_tds):
            break
        td = stat_tds[i]

        sq = td.css_first("div.stats-sq")
        if sq:
            mod_classes = sq.attributes.get("class") or ""
            if "mod-egg" in mod_classes:
                setattr(entry, field_name, None)
            else:
                setattr(entry, field_name, _parse_int(sq.text(deep=False, strip=True)))
        else:
            setattr(entry, field_name, None)

        popable = td.css_first(".wf-popable-contents")
        if popable:
            notable_rounds = _parse_notable_rounds(popable, player_mapping)
            setattr(entry, rounds_field, notable_rounds)

    if len(tds) > 11:
        econ_sq = tds[11].css_first("div.stats-sq")
        if econ_sq:
            entry.econ = _parse_int(econ_sq.text(deep=False, strip=True))

    if len(tds) > 12:
        pl_sq = tds[12].css_first("div.stats-sq")
        if pl_sq:
            entry.pl = _parse_int(pl_sq.text(deep=False, strip=True))

    if len(tds) > 13:
        de_sq = tds[13].css_first("div.stats-sq")
        if de_sq:
            entry.de = _parse_int(de_sq.text(deep=False, strip=True))

    return entry


def parse_performance_data(
    html: HTMLParser, game_id: str = "all", player_mapping: dict[str, int] | None = None,
) -> PerformanceData:
    """Parse performance metrics from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.
        game_id: Game/map identifier ('all' for combined, or numeric ID).
        player_mapping: Optional mapping of player names to player IDs.

    Returns:
        PerformanceData: Parsed performance data with kill matrices and
        advanced stats.

    """
    result = PerformanceData()

    game_div = html.css_first(f'.vm-stats-game[data-game-id="{game_id}"]')
    if not game_div:
        return result

    not_available = game_div.css_first("div[style*='justify-content: center']")
    if (
        not_available
        and "not available" in (not_available.text(strip=True) or "").lower()
    ):
        return result

    normal_table = game_div.css_first("table.mod-matrix.mod-normal")
    if normal_table:
        result.all_kills_matrix = _parse_matrix_table(normal_table)

    fkfd_table = game_div.css_first("table.mod-matrix.mod-fkfd")
    if fkfd_table:
        result.first_kills_matrix = _parse_matrix_table(fkfd_table)

    op_table = game_div.css_first("table.mod-matrix.mod-op")
    if op_table:
        result.op_kills_matrix = _parse_matrix_table(op_table)

    adv_table = game_div.css_first("table.mod-adv-stats")
    if adv_table:
        rows = adv_table.css("tr")
        for tr in rows:
            tds = tr.css("td")
            if len(tds) < 3:
                continue
            entry = _parse_adv_stats_row(tr, player_mapping or {})
            if entry.name:
                result.adv_stats.append(entry)

    return result
