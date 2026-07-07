"""Player matches namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.matches.models import MatchEntry, MatchHistoryPage, PlayerMatches
from vlrdevapi._player.matches.parser import parse_player_matches
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class MatchesNamespace:
    """Access player match history from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, player_id: int, limit: int = 20) -> PlayerMatches:
        """Get match history for a player.

        Args:
            player_id: The unique player identifier on vlr.gg.
            limit: Maximum number of matches to return. Defaults to ``20``.
                If more matches are needed than fit on one page, additional
                pages are fetched automatically.

        Returns:
            PlayerMatches: An object with ``player_id`` and ``matches``
            (list of ``MatchEntry``, each with ``teams``, ``score``,
            ``map``, ``event``, ``round``, and ``result``).

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.matches(player_id=11225, limit=5)
            >>> result.matches[0].teams
            ('Sentinels', 'Fnatic')
            >>> result.matches[0].result
            'W'

        """
        matches: list[MatchEntry] = []
        page_num = 1
        while len(matches) < limit:
            page = self._fetch_page(player_id, page_num)
            matches.extend(page.matches)
            if not page.has_next_page:
                break
            page_num += 1
        return PlayerMatches(player_id=player_id, matches=matches[:limit])

    def _fetch_page(self, player_id: int, page: int) -> MatchHistoryPage:
        path = _build_path(player_id, page)
        html = self._sync._fetch(path)
        return parse_player_matches(html)


def _build_path(player_id: int, page: int = 1) -> str:
    path = f"/player/matches/{player_id}/"
    if page > 1:
        path += f"?page={page}"
    return path
