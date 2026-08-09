"""Shared helpers for series sub-namespaces."""

from selectolax.parser import HTMLParser


def _ordered_game_ids(html: HTMLParser) -> list[str]:
    """Return the real VLR game IDs in map order from the series nav tabs.

    The stats nav renders one item per map, always starting with the
    "All Maps" item (``mod-all``), followed by each map in play order.
    Each item carries the real VLR ``data-game-id``.

    Args:
        html: Parsed series stats page (overview, performance, or economy).

    Returns:
        list[str]: Real game IDs in map order, e.g. ``['233478', ...]``.

    """
    ids: list[str] = []
    for el in html.css(".vm-stats-gamesnav-item.js-map-switch"):
        if "mod-all" in (el.attributes.get("class") or ""):
            continue
        gid = (el.attributes.get("data-game-id") or "").strip()
        if gid:
            ids.append(gid)
    return ids


def resolve_game_id(html: HTMLParser, game_id: int | str) -> str:
    """Resolve a user-supplied game identifier to a real VLR game ID.

    Accepts either of the following:

    - ``"all"``: aggregate across the whole series (returned unchanged).
    - A 1-based game number (e.g. ``1``): the first map played in the
      series, resolved from the stats nav tabs.
    - A real VLR game ID (e.g. ``"233478"``): passed through unchanged.

    Args:
        html: Parsed series stats page containing the game nav tabs.
        game_id: User-supplied game identifier.

    Returns:
        str: Real VLR game ID (or ``"all"``) to use for selectors/URLs.

    """
    as_str = str(game_id).strip()
    if as_str.lower() == "all":
        return "all"

    real_ids = _ordered_game_ids(html)
    if as_str in real_ids:
        return as_str

    try:
        index = int(game_id)
    except (TypeError, ValueError):
        return as_str

    if 1 <= index <= len(real_ids):
        return real_ids[index - 1]

    return as_str


class PlayerMap:
    """Resolve VLR player names to player IDs using team + name keys.

    The series "performance" tab renders player cells without any links,
    so player IDs are recovered from the series "overview" tab and looked
    up here. Keys are (team_short, name) pairs, which are unique within a
    match; a name-only fallback covers cells that lack team context (e.g.
    notable-round victim lists).

    """

    def __init__(
        self,
        mapping: dict[tuple[str, str], int] | dict[str, int] | None = None,
    ):
        self._by_team_name: dict[tuple[str, str], int] = {}
        self._by_name: dict[str, int] = {}
        if not mapping:
            return
        for key, player_id in mapping.items():
            if isinstance(key, str):
                self.add("", key, player_id)
            else:
                team_short, name = key
                self.add(team_short, name, player_id)

    def add(self, team_short: str, name: str, player_id: int) -> None:
        """Register a player.

        Args:
            team_short: The player's team abbreviation.
            name: The player's in-game name.
            player_id: The player's VLR player ID.

        """
        team_short = (team_short or "").strip()
        name = (name or "").strip()
        if not name:
            return
        self._by_team_name[(team_short, name)] = player_id
        self._by_name.setdefault(name, player_id)

    def get(self, name: str, team_short: str = "") -> int | None:
        """Return the player ID for a name, optionally within a team.

        Args:
            name: The player's in-game name.
            team_short: The player's team abbreviation, if known.

        Returns:
            int | None: The player ID, or None if unknown.

        """
        name = (name or "").strip()
        team_short = (team_short or "").strip()
        if not name:
            return None
        if team_short:
            player_id = self._by_team_name.get((team_short, name))
            if player_id is not None:
                return player_id
        return self._by_name.get(name)

    def __bool__(self) -> bool:
        return bool(self._by_name)

    def __len__(self) -> int:
        return len(self._by_name)
