"""Team stats namespace."""

from datetime import date, timedelta

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.info.namespace import SeriesInfoNamespace
from vlrdevapi._team.stats.models import AgentCompositionLevel, TeamStats
from vlrdevapi._team.stats.parser import parse_team_stats
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


def _build_stats_url(
    team_id: int,
    date_start: date | None = None,
    date_end: date | None = None,
    event_id: int | None = None,
    series_id: int | None = None,
    subseries_id: int | None = None,
    last_days: int | None = None,
) -> str:
    today = date.today()

    if last_days is not None:
        date_end = today
        date_start = today - timedelta(days=last_days)
    else:
        if date_end is None:
            date_end = today
        if date_start is None:
            date_start = today - timedelta(days=30)

    params = []
    if event_id is not None:
        params.append(f"event_id={event_id}")
    if series_id is not None:
        params.append(f"series_id={series_id}")
    if subseries_id is not None:
        params.append(f"subseries_id={subseries_id}")
    params.append(f"date_start={date_start.strftime('%Y-%m-%d')}")
    params.append(f"date_end={date_end.strftime('%Y-%m-%d')}")

    query_string = "&".join(params)
    return f"/team/stats/{team_id}/?{query_string}"


class TeamStatsNamespace:
    """Access team map statistics from vlr.gg."""

    __slots__ = ("_series_info", "_sync")

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._series_info = SeriesInfoNamespace(client, timeout, retry_config, rate_limiter)

    @sanitize_and_validate
    def __call__(
        self,
        team_id: int,
        date_start: date | None = None,
        date_end: date | None = None,
        event_id: int | None = None,
        series_id: int | None = None,
        subseries_id: int | None = None,
        last_days: int | None = None,
        agent_composition: AgentCompositionLevel = "none",
    ) -> TeamStats:
        """Get map and agent statistics for a team.

        Args:
            team_id: Unique team identifier on vlr.gg.
            date_start: Start date for stats (inclusive). Defaults to 30 days ago.
            date_end: End date for stats (inclusive). Defaults to today.
            event_id: Filter stats to a specific event.
            series_id: Filter stats to a specific series.
            subseries_id: Filter stats to a specific sub-series.
            last_days: Shorthand to set date range to the last N days.
            agent_composition: Agent composition detail level.
                ``"none"`` (default), ``"composition"``, or ``"detailed"``.

        Returns:
            TeamStats: Map-level statistics including ``maps``, ``rounds_won``,
            ``rounds_lost``, ``kills``, ``deaths``, ``assists``, ``acs``,
            ``kast``, and per-map agent composition data when requested.

        Raises:
            ValidationError: If ``team_id`` is not a valid positive integer.
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.team.stats(team_id=4568, last_days=90)
            >>> result.maps[0].win_rate
            66.7

        """
        path = _build_stats_url(
            team_id=team_id, date_start=date_start, date_end=date_end,
            event_id=event_id, series_id=series_id,
            subseries_id=subseries_id, last_days=last_days,
        )
        html = self._sync._fetch(path)
        return parse_team_stats(
            html, team_id,
            agent_composition=agent_composition,
            series_info_fn=self._series_info if agent_composition == "detailed" else None,
        )

