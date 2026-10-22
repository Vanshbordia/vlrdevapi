"""Team completed matches namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._cache import LRUCache
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._team.completed_matches.models import (
    OpponentInCompletedMatch,
    TeamCompletedMatchEntry,
    TeamCompletedMatches,
)
from vlrdevapi._team.completed_matches.parser import (
    parse_team_completed_matches,
)
from vlrdevapi._utils.paths import team_matches as team_matches_path
from vlrdevapi._utils.team_enrichment import enrich_team_match_sync
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
    fetch_sync,
)
from vlrdevapi.validators import sanitize_and_validate


class TeamCompletedMatchesNamespace:
    """Access completed matches for a team from vlr.gg."""

    __slots__ = ("_series_info", "_source_tz", "_sync", "_team_cache")

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
        self._series_info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._team_cache: LRUCache[int, dict[str, str]] = LRUCache[int, dict[str, str]](maxsize=256)

    @sanitize_and_validate
    def __call__(
        self,
        team_id: int,
        limit: int = 50,
        return_all: bool = False,
    ) -> TeamCompletedMatches:
        """Get completed matches for a team.

        Args:
            team_id: The unique team identifier on vlr.gg.
            limit: Maximum number of completed matches to return. Defaults to
                ``50``, which is the size of the first VLR page. Additional
                pages are fetched only when needed to satisfy the limit, so
                ``limit=80`` fetches two pages and returns the first 80.
            return_all: If ``True``, fetch every page and return all matches.
                This overrides ``limit``.

        Returns:
            TeamCompletedMatches: Completed matches with ``match_id``, ``event_name``, ``opponent``, ``score``, ``rounds_won``, ``rounds_lost``, ``stage``, and enrichment data (team IDs, series info). ``has_next_page`` indicates whether more matches exist.

        Raises:
            ValidationError: If ``team_id`` or ``limit`` are not valid positive integers.
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.team.completed_matches(team_id=4568)
            >>> result.matches[0].score
            '2-1'
            >>> result = vlrdevapi.team.completed_matches(team_id=4568, return_all=True)

        """
        result = TeamCompletedMatches(team_id=team_id)
        page = 1

        while True:
            page_result = parse_team_completed_matches(
                self._sync._fetch(_completed_matches_path(team_id, page)),
                team_id,
                source_tz=self._source_tz,
            )
            result.matches.extend(page_result.matches)
            result.has_next_page = page_result.has_next_page

            if return_all:
                if not page_result.has_next_page:
                    break
            elif len(result.matches) >= limit or not page_result.has_next_page:
                break

            page += 1

        if return_all:
            result.has_next_page = False
        else:
            result.matches = result.matches[:limit]

        if not result.matches:
            return result

        _tid = team_id
        _cache = self._team_cache
        _timeout = self._sync._timeout
        _rc = self._sync._retry_config
        _rl = self._sync._rate_limiter

        def _do_enrich(match: TeamCompletedMatchEntry, client: httpx.Client) -> None:
            local_series_info = SeriesInfoNamespace(client, _timeout, _rc, _rl)
            enrich_team_match_sync(
                match, _tid,
                series_info_fn=lambda match_id: local_series_info(match_id),  # type: ignore
                fetch_fn=lambda p: fetch_sync(client, p, _timeout, retry_config=_rc, rate_limiter=_rl),
                team_cache=_cache,
                opponent_cls=OpponentInCompletedMatch,
                log_label="completed",
            )

        self._sync._parallel_enrich(result.matches, _do_enrich, max_workers=5)
        return result


def _completed_matches_path(team_id: int, page: int) -> str:
    path = f"{team_matches_path(team_id)}/?core_id=all&group=completed"
    if page > 1:
        path += f"&page={page}"
    return path

