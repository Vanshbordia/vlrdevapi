import logging
import re
from collections.abc import Callable

from selectolax.parser import HTMLParser, Node

from vlrdevapi._series.info.models import SeriesInfo
from vlrdevapi._team.stats.models import (
    AgentComposition,
    AgentCompositionLevel,
    CompositionMatchDetails,
    MapStats,
    TeamStats,
)
from vlrdevapi.exceptions import VlrdevapiException

logger = logging.getLogger(__name__)

_AGENT_NAME_OVERRIDES: dict[str, str] = {
    "kay\\o": "Kayo",
    "kayo": "Kayo",
}


def _parse_percentage(value: str) -> float | None:
    if not value or value.strip() == "-":
        return None
    value = value.strip().replace("%", "")
    try:
        return float(value)
    except ValueError:
        return None


def _parse_int(value: str) -> int | None:
    if not value or value.strip() == "-":
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _extract_cell_text(cell: Node) -> str:
    return cell.text(strip=True)


def _parse_map_name(text: str) -> tuple[str, int]:
    match = re.match(r"^(.+?)\s*\((\d+)\)$", text.strip())
    if match:
        return match.group(1).strip(), int(match.group(2))
    return text.strip(), 0


def _normalize_agent_name(src_path: str) -> str:
    filename = src_path.rsplit("/", maxsplit=1)[-1]
    name = filename.replace(".png", "").replace(".webp", "").replace("-", " ")
    lower_name = name.lower()
    if lower_name in _AGENT_NAME_OVERRIDES:
        return _AGENT_NAME_OVERRIDES[lower_name]
    return name.title()


def _parse_compositions_from_cell(cell: Node) -> dict[str, AgentComposition]:
    compositions: dict[str, AgentComposition] = {}

    for agg_div in cell.css(".agent-comp-agg"):
        comp_hash = agg_div.attributes.get("data-agent-comp-hash", "")
        if not comp_hash:
            continue

        play_count = 0
        for span in agg_div.css("span"):
            text = span.text(strip=True)
            match = re.match(r"\((\d+)\)", text)
            if match:
                play_count = int(match.group(1))
                break

        agent_names: list[str] = []
        for img in agg_div.css("img"):
            src = img.attributes.get("src", "")
            if src:
                agent_names.append(_normalize_agent_name(src))

        agent_names.sort()

        compositions[comp_hash] = AgentComposition(
            agents=agent_names,
            games_played=play_count,
            wins=0,
            losses=0,
            win_rate=0.0,
            matches=None,
        )

    return compositions


def _parse_score(score_text: str) -> tuple[int, int]:
    parts = score_text.split("/")
    if len(parts) == 2:
        a = _parse_int(parts[0])
        b = _parse_int(parts[1])
        return (a if a is not None else 0), (b if b is not None else 0)
    return 0, 0


def _parse_game_rows(html: HTMLParser, map_name: str) -> list[dict]:
    games: list[dict] = []

    for row in html.css(f"tr.mod-toggle.mod-{map_name}"):
        cells = row.css("td")
        if len(cells) < 3:
            continue

        game_cell = None
        for cell in cells:
            classes = (cell.attributes.get("class") or "").split()
            if "mod-win" in classes or "mod-loss" in classes:
                game_cell = cell
                break

        if not game_cell:
            continue

        is_win = "mod-win" in (game_cell.attributes.get("class") or "").split()

        link = game_cell.css_first("a")
        if not link:
            continue

        href = link.attributes.get("href", "") or ""
        series_id = 0
        href_match = re.match(r"/(\d+)/", href)
        if href_match:
            series_id = int(href_match.group(1))

        date_div = link.css_first("div")
        date = date_div.text(strip=True) if date_div else ""

        opponent_name = ""
        opponent_div = link.css_first(".text-of")
        if opponent_div:
            opponent_name = opponent_div.text(strip=True)

        score_div = link.css_first(".game-score")
        team_score, opponent_score = 0, 0
        if score_div:
            team_score, opponent_score = _parse_score(score_div.text(strip=True))

        attack_won, attack_lost = 0, 0
        defense_won, defense_lost = 0, 0
        ot_won, ot_lost = 0, 0

        half_divs = link.css(".game-half")
        for half_div in half_divs:
            label_div = half_div.css_first(".game-half-label")
            if not label_div:
                continue

            label_text = label_div.text(strip=True).lower()
            if label_text not in ("atk", "def", "ot"):
                continue

            score_text = ""
            for child in half_div.iter():
                if child.tag != "div":
                    continue
                if child is half_div:
                    continue
                child_class = child.attributes.get("class") or ""
                if "game-half-label" not in child_class:
                    score_text = child.text(strip=True)
                    break

            if not score_text:
                continue

            won, lost = _parse_score(score_text)

            if label_text == "atk":
                attack_won, attack_lost = won, lost
            elif label_text == "def":
                defense_won, defense_lost = won, lost
            elif label_text == "ot":
                ot_won, ot_lost = won, lost

        comp_hash = ""
        for cell in cells:
            classes = (cell.attributes.get("class") or "").split()
            for cls in classes:
                if len(cls) == 12:
                    is_valid_hash = True
                    for c in cls:
                        if c not in "0123456789abcdef":
                            is_valid_hash = False
                            break
                    if is_valid_hash:
                        comp_hash = cls
                        break
            if comp_hash:
                break

        games.append(
            {
                "composition_hash": comp_hash,
                "is_win": is_win,
                "date": date,
                "opponent_name": opponent_name,
                "team_score": team_score,
                "opponent_score": opponent_score,
                "attack_rounds_won": attack_won,
                "attack_rounds_lost": attack_lost,
                "defense_rounds_won": defense_won,
                "defense_rounds_lost": defense_lost,
                "ot_rounds_won": ot_won,
                "ot_rounds_lost": ot_lost,
                "series_id": series_id,
            },
        )

    return games


def _sort_compositions(compositions: list[AgentComposition]) -> list[AgentComposition]:
    return sorted(compositions, key=lambda c: (-c.games_played, -c.win_rate))


def _build_match_details(
    game: dict,
    series_info,
    is_win: bool,
) -> CompositionMatchDetails:
    details = CompositionMatchDetails(
        series_id=game.get("series_id", 0),
        date=game.get("date", ""),
        opponent_id=0,
        opponent_name=game.get("opponent_name", ""),
        opponent_tag="",
        team_score=game.get("team_score", 0),
        opponent_score=game.get("opponent_score", 0),
        is_win=is_win,
        attack_rounds_won=game.get("attack_rounds_won", 0),
        attack_rounds_lost=game.get("attack_rounds_lost", 0),
        defense_rounds_won=game.get("defense_rounds_won", 0),
        defense_rounds_lost=game.get("defense_rounds_lost", 0),
        ot_rounds_won=game.get("ot_rounds_won", 0),
        ot_rounds_lost=game.get("ot_rounds_lost", 0),
        event_id=0,
        event_name="",
        stage="",
        patch="",
        series_result="",
    )

    if series_info:
        details.event_id = series_info.event_id
        details.event_name = series_info.event_name
        details.stage = series_info.stage
        details.patch = series_info.patch

        opponent_name_lower = game.get("opponent_name", "").lower()
        if series_info.team1 and opponent_name_lower == series_info.team1.name.lower():
            details.opponent_id = series_info.team1.id
            details.opponent_name = series_info.team1.name
            details.opponent_tag = series_info.team1.tag
        elif series_info.team2 and opponent_name_lower == series_info.team2.name.lower():
            details.opponent_id = series_info.team2.id
            details.opponent_name = series_info.team2.name
            details.opponent_tag = series_info.team2.tag

        details.series_result = "won" if is_win else "lost"

    return details


def _parse_map_row_basic(row: Node) -> MapStats | None:
    cells = row.css("td")
    if len(cells) < 12:
        return None

    map_cell = cells[0]
    map_text = _extract_cell_text(map_cell)
    map_name, games_played = _parse_map_name(map_text)

    if games_played == 0:
        return None

    stats = MapStats()
    stats.map_name = map_name
    stats.games_played = games_played
    stats.win_rate = _parse_percentage(_extract_cell_text(cells[2]))
    stats.wins = _parse_int(_extract_cell_text(cells[3]))
    stats.losses = _parse_int(_extract_cell_text(cells[4]))
    stats.attack_first = _parse_int(_extract_cell_text(cells[5]))
    stats.defense_first = _parse_int(_extract_cell_text(cells[6]))
    stats.attack_round_win_rate = _parse_percentage(_extract_cell_text(cells[7]))
    stats.attack_rounds_won = _parse_int(_extract_cell_text(cells[8]))
    stats.attack_rounds_lost = _parse_int(_extract_cell_text(cells[9]))
    stats.defense_round_win_rate = _parse_percentage(_extract_cell_text(cells[10]))
    stats.defense_rounds_won = _parse_int(_extract_cell_text(cells[11]))
    stats.defense_rounds_lost = _parse_int(_extract_cell_text(cells[12]))

    return stats


def _parse_map_row_with_compositions(
    html: HTMLParser,
    row: Node,
) -> tuple[MapStats | None, list[dict], dict[str, AgentComposition]]:
    cells = row.css("td")
    if len(cells) < 12:
        return None, [], {}

    map_cell = cells[0]
    map_text = _extract_cell_text(map_cell)
    map_name, games_played = _parse_map_name(map_text)

    if games_played == 0:
        return None, [], {}

    stats = MapStats()
    stats.map_name = map_name
    stats.games_played = games_played
    stats.win_rate = _parse_percentage(_extract_cell_text(cells[2]))
    stats.wins = _parse_int(_extract_cell_text(cells[3]))
    stats.losses = _parse_int(_extract_cell_text(cells[4]))
    stats.attack_first = _parse_int(_extract_cell_text(cells[5]))
    stats.defense_first = _parse_int(_extract_cell_text(cells[6]))
    stats.attack_round_win_rate = _parse_percentage(_extract_cell_text(cells[7]))
    stats.attack_rounds_won = _parse_int(_extract_cell_text(cells[8]))
    stats.attack_rounds_lost = _parse_int(_extract_cell_text(cells[9]))
    stats.defense_round_win_rate = _parse_percentage(_extract_cell_text(cells[10]))
    stats.defense_rounds_won = _parse_int(_extract_cell_text(cells[11]))
    stats.defense_rounds_lost = _parse_int(_extract_cell_text(cells[12]))

    game_rows: list[dict] = []
    compositions: dict[str, AgentComposition] = {}

    if len(cells) >= 14:
        comp_cell = cells[13]
        compositions = _parse_compositions_from_cell(comp_cell)
        if compositions:
            game_rows = _parse_game_rows(html, map_name)

    return stats, game_rows, compositions


def _apply_basic_enrichment(
    stats: MapStats,
    game_rows: list[dict],
    compositions: dict[str, AgentComposition],
) -> None:
    for game in game_rows:
        comp_hash = game.get("composition_hash", "")
        if not comp_hash or comp_hash not in compositions:
            continue
        comp = compositions[comp_hash]
        if game.get("is_win"):
            comp.wins += 1
        else:
            comp.losses += 1

    for comp in compositions.values():
        total = comp.wins + comp.losses
        if total > 0:
            comp.win_rate = round((comp.wins / total) * 100, 2)

    stats.compositions = _sort_compositions(list(compositions.values()))


def _apply_detailed_enrichment(
    stats: MapStats,
    game_rows: list[dict],
    compositions: dict[str, AgentComposition],
    series_info_fn: Callable[[int], SeriesInfo] | None,
) -> None:
    for game in game_rows:
        comp_hash = game.get("composition_hash", "")
        if not comp_hash or comp_hash not in compositions:
            continue

        comp = compositions[comp_hash]
        is_win = game.get("is_win", False)

        if is_win:
            comp.wins += 1
        else:
            comp.losses += 1

        if comp.matches is None:
            comp.matches = []

        series_id = game.get("series_id", 0)
        series_info = None
        if series_info_fn is not None:
            try:
                series_info = series_info_fn(series_id)
            except VlrdevapiException:
                logger.warning("Failed to fetch series info for series %d", series_id)
                raise

        match_details = _build_match_details(game, series_info, is_win)
        comp.matches.append(match_details)

    for comp in compositions.values():
        total = comp.wins + comp.losses
        if total > 0:
            comp.win_rate = round((comp.wins / total) * 100, 2)

    stats.compositions = _sort_compositions(list(compositions.values()))


def _parse_all_map_rows(
    html: HTMLParser,
    team_id: int,
    agent_composition: AgentCompositionLevel,
) -> tuple[list[MapStats], list[tuple[MapStats, list[dict], dict[str, AgentComposition]]]]:
    """Parse all map rows from the stats table.

    Args:
        html: Parsed HTML of the team stats page.
        team_id: The team identifier.
        agent_composition: Agent composition detail level.

    Returns:
        tuple: A pair ``(basic_stats, pending)`` where ``basic_stats`` is
        a list of fully parsed ``MapStats`` objects, and ``pending`` contains
        tuples of ``(MapStats, game_rows, compositions)`` that still need
        enrichment for detailed agent composition data.

    """
    basic_stats: list[MapStats] = []
    pending: list[tuple[MapStats, list[dict], dict[str, AgentComposition]]] = []

    table = html.css_first("table.wf-table.mod-team-maps")
    if not table:
        return basic_stats, pending

    tbody = table.css_first("tbody")
    if not tbody:
        return basic_stats, pending

    for row in tbody.css("tr"):
        classes = (row.attributes.get("class") or "").split()
        if "mod-toggle" in classes:
            continue

        if agent_composition == "none":
            map_stats = _parse_map_row_basic(row)
            if map_stats:
                basic_stats.append(map_stats)
            continue

        stats, game_rows, compositions = _parse_map_row_with_compositions(html, row)
        if stats is None:
            continue

        if not compositions:
            basic_stats.append(stats)
        elif agent_composition == "basic":
            _apply_basic_enrichment(stats, game_rows, compositions)
            basic_stats.append(stats)
        else:
            pending.append((stats, game_rows, compositions))

    return basic_stats, pending


def parse_team_stats(
    html: HTMLParser,
    team_id: int,
    agent_composition: AgentCompositionLevel = "none",
    series_info_fn: Callable[[int], SeriesInfo] | None = None,
) -> TeamStats:
    """Parse team stats from HTML.

    Args:
        html: Parsed HTML of the team stats page.
        team_id: The team identifier.
        agent_composition: Agent composition detail level.
            ``"none"`` (default), ``"basic"``, or ``"detailed"``.
        series_info_fn: Callable to fetch series info for detailed
            enrichment. Required when ``agent_composition="detailed"``.

    Returns:
        TeamStats: Parsed team statistics including per-map stats and
        optional agent composition data.

    """
    result = TeamStats(team_id=team_id)
    basic_stats, pending = _parse_all_map_rows(html, team_id, agent_composition)

    result.maps.extend(basic_stats)

    for stats, game_rows, compositions in pending:
        _apply_detailed_enrichment(stats, game_rows, compositions, series_info_fn)
        result.maps.append(stats)

    return result



