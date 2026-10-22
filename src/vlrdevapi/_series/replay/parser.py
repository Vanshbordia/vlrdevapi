"""Series replay parser — extracts the per-round kill-feed timeline.

Layout on the ``tab=logs`` page:

- one ``div.lg-round`` block per round, each fully embedded in the HTML;
- inside every block, one ``div.lg-map`` holding the ``data-map`` JSON
  blob with the round's players and per-event geometry, plus one
  ``div.lg-row`` feed row per event.

The JSON events and the feed rows pair up 1:1 by index (verified across
multiple series), so the parser walks them in lockstep; row attributes
contribute only the kill cause and the spike site.
"""

import json
import math
from html import unescape

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._series._utils import resolve_game_id
from vlrdevapi._series.replay.models import (
    ReplayActor,
    ReplayAlivePlayer,
    ReplayData,
    ReplayEvent,
    ReplayEventType,
    ReplayPlayerRef,
    ReplayRound,
)


def _actor(info: tuple | None, team_names: dict[int, str], atk: int) -> ReplayActor | None:
    """Build a ReplayActor from a players-map entry ``(team, agent, name)``."""
    if info is None:
        return None
    team_no, agent, name = info
    return ReplayActor(
        name=str(name),
        agent=str(agent),
        team=team_names.get(team_no, ""),
        side="Attack" if team_no == atk else "Defense" if atk else "",
    )


def _alive_snapshot(
    locs: list,
    players: dict[int, tuple],
    team_names: dict[int, str],
    atk: int,
) -> list[ReplayAlivePlayer]:
    """Build the alive-player snapshot from one event's ``locs`` rows."""
    snapshot: list[ReplayAlivePlayer] = []
    for loc in locs:
        if not isinstance(loc, list) or len(loc) < 3:
            continue
        info = players.get(int(loc[0]))
        if info is None:
            continue
        team_no, agent, name = info
        snapshot.append(
            ReplayAlivePlayer(
                name=str(name),
                agent=str(agent),
                team=team_names.get(team_no, ""),
                side="Attack" if team_no == atk else "Defense" if atk else "",
                x=float(loc[1]),
                y=float(loc[2]),
                view_angle=int(loc[3]) if len(loc) > 3 else 0,
            ),
        )
    return snapshot


def _load_map_data(value: str) -> dict:
    """Decode the ``data-map`` JSON blob.

    Attribute entities are normally already decoded; unescape as a
    fallback.

    """
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return json.loads(unescape(value))


def _team_labels(round_div: Node) -> tuple[str, str]:
    """Extract ``(team1, team2)`` names from the round's scoreboard band."""
    t1 = t2 = ""
    for team_el in round_div.css("span.lg-band-team"):
        classes = team_el.attributes.get("class") or ""
        name_el = team_el.css_first("span.lg-band-name")
        if name_el is None:
            continue
        label = name_el.attributes.get("title") or name_el.text(strip=True)
        if "mod-t1" in classes:
            t1 = label
        elif "mod-t2" in classes:
            t2 = label
    return t1, t2


def _build_real_event(
    event: dict,
    row: Node | None,
    players: dict[int, tuple],
    team_names: dict[int, str],
    atk: int,
) -> ReplayEvent:
    """Build one logged event from its JSON blob plus its feed row."""
    event_type = str(event.get("type") or "")
    locs = event.get("locs") or []
    alive = _alive_snapshot(locs, players, team_names, atk)

    try:
        by_key = int(event["by"]) if "by" in event and event["by"] is not None else None
    except (ValueError, TypeError):
        by_key = None
    actor = _actor(players.get(by_key) if by_key is not None else None, team_names, atk)
    victim = None
    pos = event.get("pos")
    from_pos = event.get("from")
    distance: float | None = None

    if event_type == "kill":
        try:
            vid_key = int(event["vid"]) if "vid" in event and event["vid"] is not None else None
        except (ValueError, TypeError):
            vid_key = None
        victim = _actor(players.get(vid_key) if vid_key is not None else None, team_names, atk)
        if (
            isinstance(from_pos, list)
            and len(from_pos) >= 2
            and isinstance(pos, list)
            and len(pos) >= 2
        ):
            distance = math.dist((float(from_pos[0]), float(from_pos[1])), (float(pos[0]), float(pos[1])))

    site = ""
    if row is not None and event_type in ("plant", "defuse"):
        site_el = row.css_first("span.lg-site-text")
        if site_el is not None:
            site = site_el.text(strip=True)

    cause = ""
    if row is not None and event_type == "kill":
        source_el = row.css_first("span.lg-source")
        if source_el is not None:
            cause = source_el.attributes.get("title") or ""

    return ReplayEvent(
        type=_EVENT_ENUMS.get(event_type, ReplayEventType.KILL),
        clock=str(event.get("t") or ""),
        seconds=_clock_seconds(str(event.get("t") or "")),
        actor=actor,
        victim=victim,
        cause=cause,
        site=site,
        pos_x=float(pos[0]) if isinstance(pos, list) and len(pos) >= 2 else None,
        pos_y=float(pos[1]) if isinstance(pos, list) and len(pos) >= 2 else None,
        from_x=float(from_pos[0]) if isinstance(from_pos, list) and len(from_pos) >= 2 else None,
        from_y=float(from_pos[1]) if isinstance(from_pos, list) and len(from_pos) >= 2 else None,
        distance_units=distance,
        alive=alive,
    )


_EVENT_ENUMS = {
    "kill": ReplayEventType.KILL,
    "plant": ReplayEventType.PLANT,
    "defuse": ReplayEventType.DEFUSE,
}


def _clock_seconds(clock: str) -> int | None:
    """Convert an ``M:SS`` round clock to integer seconds."""
    try:
        minutes, secs = clock.split(":")
        return int(minutes) * 60 + int(secs)
    except ValueError:
        return None


def _parse_round(round_div: Node, team1: str, team2: str) -> ReplayRound | None:
    """Parse one ``div.lg-round`` block into a ReplayRound.

    Returns ``None`` when the round block carries no embedded data map
    (round data can be missing on vlr.gg even for played maps).
    """
    round_data = ReplayRound(
        round_number=int(round_div.attributes.get("data-round") or "0"),
        attacking="",
    )

    map_div = round_div.css_first("div.lg-map")
    if map_div is None:
        return None
    data = _load_map_data(map_div.attributes.get("data-map") or "")
    if not data:
        return None

    team_names = {1: team1, 2: team2}
    players: dict[int, tuple] = {}
    for key, value in (data.get("players") or {}).items():
        if isinstance(value, list) and len(value) >= 3:
            players[int(key)] = (int(value[0]), str(value[1]), str(value[2]))

    atk = int(data.get("atk") or 0)
    round_data.attacking = team_names.get(atk, "")
    round_data.players = [
        ReplayPlayerRef(
            name=info[2],
            agent=info[1],
            team=team_names.get(info[0], ""),
            side="Attack" if info[0] == atk else "Defense" if atk else "",
        )
        for info in players.values()
    ]

    events_raw = data.get("events") or []
    boom_at = data.get("boom")
    round_data.boom_at = int(boom_at) if isinstance(boom_at, (int, float)) else None

    rows_by_ev: dict[int, Node] = {}
    for row in round_div.css("div.lg-row"):
        raw_ev = row.attributes.get("data-ev")
        if raw_ev is not None:
            rows_by_ev[int(raw_ev)] = row

    # Derived entries keyed by the slot they are inserted before.
    derived_by_slot: dict[int, list[ReplayEvent]] = {}

    # Resurrections: a player recorded dead earlier in the round shows up
    # alive again in a later event's locs. vlr.gg emits no feed row for it.
    dead_at: dict[int, int] = {}
    for index, event in enumerate(events_raw):
        locs = event.get("locs") or []
        alive_ids = {int(loc[0]) for loc in locs if isinstance(loc, list)}
        for pid in sorted(alive_ids & dead_at.keys(), key=lambda p: dead_at[p]):
            info = players.get(pid)
            loc = next(loc for loc in locs if int(loc[0]) == pid)
            derived_by_slot.setdefault(index, []).append(
                ReplayEvent(
                    type=ReplayEventType.RESURRECT,
                    clock=str(event.get("t") or ""),
                    seconds=_clock_seconds(str(event.get("t") or "")),
                    actor=_actor(info, team_names, atk),
                    pos_x=float(loc[1]),
                    pos_y=float(loc[2]),
                    alive=_alive_snapshot(locs, players, team_names, atk),
                    derived=True,
                ),
            )
            dead_at.pop(pid)
        if event.get("type") == "kill" and event.get("vid") is not None:
            dead_at[int(event["vid"])] = index

    # Spike detonation: vlr.gg records no feed row; ``boom`` is the event
    # index at which the spike is no longer planted (the detonation sits
    # between event ``boom - 1`` and event ``boom``).
    if round_data.boom_at is not None and 0 <= round_data.boom_at <= len(events_raw):
        boom_index = round_data.boom_at
        site = ""
        spike_pos: list | None = None
        for index, event in enumerate(events_raw):
            if event.get("type") == "plant":
                spike_pos = event.get("pos")
                row = rows_by_ev.get(index)
                site_el = row.css_first("span.lg-site-text") if row else None
                if site_el is not None:
                    site = site_el.text(strip=True)
        clock = ""
        if boom_index < len(events_raw):
            clock = str(events_raw[boom_index].get("t") or "")
        derived_by_slot.setdefault(boom_index, []).append(
            ReplayEvent(
                type=ReplayEventType.BOOM,
                clock=clock,
                seconds=_clock_seconds(clock),
                site=site,
                pos_x=float(spike_pos[0]) if isinstance(spike_pos, list) and len(spike_pos) >= 2 else None,
                pos_y=float(spike_pos[1]) if isinstance(spike_pos, list) and len(spike_pos) >= 2 else None,
                derived=True,
            ),
        )

    events: list[ReplayEvent] = []
    for index, event in enumerate(events_raw):
        for derived in derived_by_slot.pop(index, []):
            derived.seq = len(events)
            events.append(derived)
        real = _build_real_event(event, rows_by_ev.get(index), players, team_names, atk)
        real.seq = len(events)
        events.append(real)

    # Slots at or beyond the event count (e.g. a spike detonating after
    # the last feed row) are appended at the end in slot order.
    for slot in sorted(derived_by_slot):
        for derived in derived_by_slot[slot]:
            derived.seq = len(events)
            events.append(derived)

    round_data.events = events
    return round_data


def parse_replay_data(html: HTMLParser, game_id: int | str = "all") -> ReplayData:
    """Parse the kill-feed replay timeline from the series logs page HTML.

    Args:
        html: The selectolax HTMLParser of the logs tab page.
        game_id: Game number within the series (1-based), or a real VLR
            game ID ("all" returns an empty timeline).

    Returns:
        ReplayData: Parsed replay timeline with ``rounds`` (one
        ``ReplayRound`` per round, each with ``events``, ``players``,
        ``attacking``, and ``boom_at``), and ``team1``/``team2`` names.

    """
    gid = resolve_game_id(html, game_id)
    if gid == "all":
        return ReplayData()

    game_div = html.css_first(f'div.vm-stats-game[data-game-id="{gid}"]')
    if not game_div:
        return ReplayData()

    round_divs = game_div.css("div.lg-round")
    if not round_divs:
        return ReplayData()

    team1, team2 = _team_labels(round_divs[0])
    rounds = [
        round_data
        for raw_round in round_divs
        if (round_data := _parse_round(raw_round, team1, team2)) is not None
    ]
    if not rounds:
        return ReplayData()

    return ReplayData(
        team1=team1,
        team2=team2,
        num_rounds=len(rounds),
        rounds=rounds,
    )
