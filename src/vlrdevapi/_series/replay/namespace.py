"""Series replay namespace."""

import contextlib
from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.players.models import PlayersStats
from vlrdevapi._series.players.parser import parse_players_stats
from vlrdevapi._series.replay.models import ReplayData
from vlrdevapi._series.replay.parser import parse_replay_data
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesReplayNamespace:
    """Access the kill-feed replay timeline for a series game from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
        source_tz: ZoneInfo | tzinfo | None = None,
    ):
        self._source_tz = source_tz
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, series_id: int, game_id: int) -> ReplayData:
        """Get the kill-feed replay timeline for a series game (logs tab).

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The game number within the series (1-based), or its
                real VLR game ID.

        Returns:
            ReplayData: Replay timeline including ``rounds`` (one
            ``ReplayRound`` per round with ``events`` - kills (killer,
            victim, weapon/ability cause, positions, distance), spike
            plants/defuses with site, the derived ``boom`` detonation
            marker, derived ``resurrect`` events, and per-event ``alive``
            snapshots with map coordinates and facing angles),
            ``attacking``, ``players``, ``boom_at``, ``team1`` and
            ``team2`` names with matching ``team1_id`` and ``team2_id``,
            and ``num_rounds``. Real player IDs are resolved from the
            game's overview tab (one extra request) and matched within
            each player's team; players that cannot be matched keep ID 0.

        Raises:
            ValidationError: If ``series_id`` or ``game_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> replay = vlrdevapi.series.replay(series_id=12345, game_id=1)
            >>> replay.num_rounds
            18
            >>> replay.rounds[0].events[0].type
            <ReplayEventType.KILL: 'kill'>

        """
        html = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=logs")
        result = parse_replay_data(html, game_id=game_id)
        result.series_id = series_id
        result.game_id = game_id

        if not result.rounds:
            # Unplayed map or missing round data: nothing to enrich.
            return result

        try:
            html_overview = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=overview")
            _attach_player_ids(result, html_overview, game_id)
        except Exception:  # noqa: BLE001, S110 - optional enrichment; degrade gracefully
            pass

        return result


def _attach_player_ids(result: ReplayData, html_overview, game_id: int) -> None:
    """Attach real vlr.gg team and player IDs from the game's overview tab.

    Team IDs come from the match header links and player IDs from the
    overview stat tables. Players are matched strictly **within their
    team** by name (the logs tab records each player's team); agents are
    never used, and a name is only used as a team-less fallback when it
    maps to exactly one player ID across the whole match - so duplicate
    names can never steal another player's ID. Unmatched players keep 0.

    Args:
        result: The ReplayData to enrich in place.
        html_overview: HTML of the game overview tab.
        game_id: User-supplied game identifier (same convention as the
            logs fetch).

    """
    stats = parse_players_stats(html_overview, game_id=str(game_id))
    _apply_id_resolution(result, stats, _header_team_pairs(html_overview))


def _header_team_pairs(html_overview) -> list[tuple[str, int]]:
    """Read ``(team_name, team_id)`` pairs from the match header links.

    Unlike the stat tables, the header links survive when vlr.gg is
    missing player stats, so team IDs degrade gracefully.

    """
    pairs: list[tuple[str, int]] = []
    for selector in (".match-header-link.mod-1", ".match-header-link.mod-2"):
        el = html_overview.css_first(selector)
        if el is None:
            continue
        team_id = 0
        parts = (el.attributes.get("href", "") or "").strip("/").split("/")
        if len(parts) >= 2:
            with contextlib.suppress(ValueError):
                team_id = int(parts[1])
        name_el = el.css_first(".wf-title-med")
        pairs.append((name_el.text(strip=True) if name_el else "", team_id))
    return pairs


def _apply_id_resolution(
    result: ReplayData,
    stats: PlayersStats,
    header_pairs: list[tuple[str, int]] | None = None,
) -> None:
    """Apply team/player ID resolution from parsed overview stats.

    Team IDs are matched from the header team records by name (stat
    tables first, then the raw header links as fallback); player
    IDs are matched within each player's team by name, falling back to
    a name only when it is unique across the match. Unmatched players
    keep ID 0.

    Args:
        result: The ReplayData to enrich in place.
        stats: Parsed overview stats (teams, IDs, player rosters).
        header_pairs: ``(team_name, team_id)`` pairs read directly from
            the match header links.

    """
    header_pairs = header_pairs or []

    def team_id_for(team_name: str) -> int:
        if not team_name:
            return 0
        key = team_name.casefold()
        for team in (stats.team1, stats.team2):
            if team.team_name and team.team_name.casefold() == key:
                return team.team_id
        for header_name, header_id in header_pairs:
            if header_name and header_name.casefold() == key:
                return header_id
        return 0

    result.team1_id = team_id_for(result.team1)
    result.team2_id = team_id_for(result.team2)

    ids_by_team: dict[str, dict[str, int]] = {}
    ids_by_name: dict[str, set[int]] = {}
    for team in (stats.team1, stats.team2):
        ids: dict[str, int] = {}
        for player in team.players:
            name_key = (player.name or "").strip().casefold()
            if not name_key or not player.player_id:
                continue
            ids[name_key] = player.player_id
            ids_by_name.setdefault(name_key, set()).add(player.player_id)
        if team.team_name:
            ids_by_team[team.team_name.casefold()] = ids

    def resolve(team: str, name: str) -> int:
        name_key = (name or "").strip().casefold()
        if not name_key:
            return 0
        team_ids = ids_by_team.get((team or "").casefold())
        if team_ids is not None and name_key in team_ids:
            return team_ids[name_key]
        candidates = ids_by_name.get(name_key)
        if candidates is not None and len(candidates) == 1:
            return next(iter(candidates))
        return 0

    for round_data in result.rounds:
        for ref in round_data.players:
            ref.player_id = resolve(ref.team, ref.name)
        for ld in round_data.loadouts:
            ld.player_id = resolve(ld.team, ld.name)
        for event in round_data.events:
            for person in (event.actor, event.victim, *event.alive):
                if person is not None:
                    person.player_id = resolve(person.team, person.name)
