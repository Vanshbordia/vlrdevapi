import re
from datetime import datetime

from selectolax.parser import HTMLParser, Node

from vlrdevapi._series.info.models import MapVeto, SeriesGame, SeriesInfo, SeriesTeam
from vlrdevapi.commons.timezone import parse_vlr_stored_datetime
import contextlib


def _parse_team_link(el: Node) -> SeriesTeam:
    """Parse a team link element into a SeriesTeam model.

    Args:
        el: The selectolax Node containing the team link.

    Returns:
        SeriesTeam: Parsed team with id, name, and logo_url.

    """
    team = SeriesTeam()
    href = el.attributes.get("href", "") or ""
    # Handle both /team/1234 and https://www.vlr.gg/team/1234/name
    m = re.search(r"/team/(\d+)", href)
    if m:
        with contextlib.suppress(ValueError):
            team.id = int(m.group(1))

    name_el = el.css_first(".wf-title-med")
    if name_el:
        team.name = name_el.text(strip=True)

    img_el = el.css_first("img")
    if img_el:
        src = img_el.attributes.get("src", "") or ""
        if src.startswith("//"):
            src = "https:" + src
        team.logo_url = src

    return team


def _parse_veto(text: str) -> list[MapVeto]:
    """Parse map veto text into a list of MapVeto entries.

    Args:
        text: Semicolon-separated veto text from the match header.

    Returns:
        list[MapVeto]: Parsed veto entries (bans, picks, decider).

    """
    result: list[MapVeto] = []
    if not text:
        return result
    segments = [s.strip() for s in text.split(";") if s.strip()]
    for seg in segments:
        if seg.endswith(" remains"):
            map_name = seg.replace(" remains", "").strip()
            result.append(MapVeto(map_name=map_name, veto_type="decider", team=""))
        else:
            for action in ("ban", "pick"):
                prefix = f" {action} "
                if prefix in seg:
                    parts = seg.split(prefix, 1)
                    team_tag = parts[0].strip()
                    map_name = parts[1].strip()
                    result.append(
                        MapVeto(map_name=map_name, veto_type=action, team=team_tag),
                    )
                    break
    return result


def parse_series_info(html: HTMLParser) -> SeriesInfo:
    """Parse series overview info from the HTML response.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        SeriesInfo: Parsed series metadata including teams, scores,
        event details, veto, and games.

    """
    info = SeriesInfo()
    header = html.css_first(".match-header")
    if not header:
        return info

    event_link = header.css_first("a.match-header-event")
    if event_link:
        href = event_link.attributes.get("href", "") or ""
        event_parts = href.strip("/").split("/")
        if len(event_parts) >= 2 and event_parts[0] == "event":
            with contextlib.suppress(ValueError):
                info.event_id = int(event_parts[1])

        bold_el = event_link.css_first("div[style*='font-weight: 700']")
        if bold_el:
            info.event_name = bold_el.text(strip=True)

        series_el = event_link.css_first(".match-header-event-series")
        if series_el:
            series_text = series_el.text(strip=True)
            if ": " in series_text:
                parts = series_text.split(": ", 1)
                info.stage = parts[0].strip()
                info.bracket = parts[1].strip()
            else:
                info.stage = series_text

    date_container = header.css_first(".match-header-date")
    if date_container:
        ts_el = date_container.css_first(".moment-tz-convert")
        if ts_el:
            ts_str = ts_el.attributes.get("data-utc-ts", "") or ""
            if ts_str:
                info.datetime = parse_vlr_stored_datetime(ts_str)

        for italic_div in date_container.css("div[style*='font-style: italic']"):
            patch_text = italic_div.text(strip=True)
            if patch_text.startswith("Patch "):
                info.patch = patch_text[6:]
            elif patch_text:
                info.patch = patch_text
            break

    link1 = header.css_first(".match-header-link.mod-1")
    if link1:
        info.team1 = _parse_team_link(link1)

    link2 = header.css_first(".match-header-link.mod-2")
    if link2:
        info.team2 = _parse_team_link(link2)

    vs_section = header.css_first(".match-header-vs")
    if vs_section:
        notes = vs_section.css(".match-header-vs-note")
        if notes:
            first_note = notes[0].text(strip=True).lower()
            if first_note == "final":
                info.status = "completed"
            elif "live" in first_note:
                info.status = "live"
            else:
                info.status = "upcoming"

        if len(notes) >= 2:
            bo_text = notes[1].text(strip=True)
            if bo_text.lower().startswith("bo"):
                with contextlib.suppress(ValueError):
                    info.best_of = int(bo_text[2:])

        score_spans = [
            s for s in vs_section.css("span[class*='match-header-vs-score-']")
            if "colon" not in (s.attributes.get("class", "") or "")
        ]
        if len(score_spans) >= 2:
            try:
                info.score1 = int(score_spans[0].text(strip=True))
                info.score2 = int(score_spans[1].text(strip=True))
            except ValueError:
                pass

    veto_el = header.css_first(".match-header-note")
    if veto_el:
        veto_text = veto_el.text(strip=True)
        info.veto = _parse_veto(veto_text)

    tags = {}
    for v in info.veto:
        if v.team and v.veto_type in ("ban", "pick"):
            tags[v.team] = v.team

    assigned: set[str] = set()
    for tag in tags:
        if tag == info.team1.name:
            info.team1.tag = tag
            assigned.add(tag)
        elif tag == info.team2.name:
            info.team2.tag = tag
            assigned.add(tag)

    remaining = [t for t in tags if t not in assigned]
    if remaining and not info.team1.tag:
        info.team1.tag = remaining[0]
        assigned.add(remaining[0])
        remaining = remaining[1:]
    if remaining and not info.team2.tag:
        info.team2.tag = remaining[0]

    if not info.team1.tag and len(info.team1.name) <= 3:
        info.team1.tag = info.team1.name
    if not info.team2.tag and len(info.team2.name) <= 3:
        info.team2.tag = info.team2.name

    info.games = _parse_games(html, info)

    return info


def _parse_duration(duration_str: str) -> int | None:
    """Parse a duration string like '53:03' or '1:03:33' into total seconds.

    Args:
        duration_str: Duration string in mm:ss or h:mm:ss format.

    Returns:
        int | None: Total seconds, or None if parsing fails.

    """
    parts = duration_str.strip().split(":")
    if len(parts) == 2:
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            return None
    elif len(parts) == 3:
        try:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except ValueError:
            return None
    return None


def _parse_game_scores(html: HTMLParser) -> dict[int, dict]:
    """Parse scores, attack/defense rounds, and duration from game headers.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        dict[int, dict]: Mapping of game_id -> dict with score data.

    """
    result: dict[int, dict] = {}
    for container in html.css(".vm-stats-game[data-game-id]"):
        game_id_str = container.attributes.get("data-game-id", "") or ""
        if game_id_str == "all":
            continue
        try:
            game_id = int(game_id_str)
        except ValueError:
            continue

        header = container.css_first(".vm-stats-game-header")
        if not header:
            continue

        data: dict = {}

        left_team = header.css_first(".team")
        if left_team:
            score_el = left_team.css_first(".score")
            if score_el:
                with contextlib.suppress(ValueError):
                    data["team1_score"] = int(score_el.text(strip=True))
            ct_el = left_team.css_first("span.mod-ct")
            if ct_el:
                with contextlib.suppress(ValueError):
                    data["team1_defense_rounds"] = int(ct_el.text(strip=True))
            t_el = left_team.css_first("span.mod-t")
            if t_el:
                with contextlib.suppress(ValueError):
                    data["team1_attack_rounds"] = int(t_el.text(strip=True))
            ot_el = left_team.css_first("span.mod-ot")
            if ot_el:
                with contextlib.suppress(ValueError):
                    data["team1_overtime_rounds"] = int(ot_el.text(strip=True))

        duration_el = header.css_first(".map-duration")
        if duration_el:
            data["duration_seconds"] = _parse_duration(duration_el.text(strip=True))

        right_team = header.css_first(".team.mod-right")
        if right_team:
            score_el = right_team.css_first(".score")
            if score_el:
                with contextlib.suppress(ValueError):
                    data["team2_score"] = int(score_el.text(strip=True))
            t_el = right_team.css_first("span.mod-t")
            if t_el:
                with contextlib.suppress(ValueError):
                    data["team2_attack_rounds"] = int(t_el.text(strip=True))
            ct_el = right_team.css_first("span.mod-ct")
            if ct_el:
                with contextlib.suppress(ValueError):
                    data["team2_defense_rounds"] = int(ct_el.text(strip=True))
            ot_el = right_team.css_first("span.mod-ot")
            if ot_el:
                with contextlib.suppress(ValueError):
                    data["team2_overtime_rounds"] = int(ot_el.text(strip=True))

        result[game_id] = data

    return result


def _parse_games(html: HTMLParser, info: SeriesInfo) -> list[SeriesGame]:
    """Parse game/map entries from the series navigation tabs.

    Args:
        html: The selectolax HTMLParser of the series page.
        info: Partially parsed SeriesInfo used for veto cross-reference.

    Returns:
        list[SeriesGame]: Parsed game entries with map names, order, and
        pick info.

    """
    games: list[SeriesGame] = []
    nav_items = html.css(".vm-stats-gamesnav-item.js-map-switch")
    for el in nav_items:
        if "mod-all" in (el.attributes.get("class") or ""):
            continue

        game = SeriesGame()

        game_id_str = el.attributes.get("data-game-id", "") or ""
        if game_id_str:
            with contextlib.suppress(ValueError):
                game.game_id = int(game_id_str)

        disabled_str = el.attributes.get("data-disabled", "") or "0"
        game.played = disabled_str != "1"

        map_div = el.css_first("div[style*='text-align: center']")
        if map_div:
            span_el = map_div.css_first("span")
            if span_el:
                with contextlib.suppress(ValueError):
                    game.order = int(span_el.text(strip=True))
            map_text = map_div.text(strip=True)
            if span_el:
                order_str = span_el.text(strip=True)
                map_text = map_text[len(order_str) :].strip()
            game.map_name = map_text

        raw_html = el.html or ""
        pick_match = re.search(r"Pick:\s*(\S+)", raw_html)
        if pick_match:
            game.picked_by = pick_match.group(1)

        if not game.picked_by and game.map_name:
            for v in info.veto:
                if v.veto_type == "pick" and v.map_name == game.map_name:
                    game.picked_by = v.team
                    break

        games.append(game)

    # Enrich with scores, attack/defense rounds, and duration from game headers
    game_scores = _parse_game_scores(html)
    for game in games:
        data = game_scores.get(game.game_id)
        if data:
            for key, value in data.items():
                setattr(game, key, value)

    return games
