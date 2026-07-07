"""Series rounds namespace."""

import httpx
from selectolax.parser import HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.info.parser import parse_series_info
from vlrdevapi._series.rounds.models import RoundsData
from vlrdevapi._series.rounds.parser import parse_rounds_data
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesRoundsNamespace:
    """Access round-by-round data for a series game from vlr.gg."""

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
    def __call__(self, series_id: int, game_id: int) -> RoundsData:
        """Get round-by-round data for a series game on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The unique game/map identifier on vlr.gg.

        Returns:
            RoundsData: Round-by-round data including ``rounds``
            (list of ``RoundDetail`` with economy, damage, and kill events),
            ``team_defense``, ``team_attack``, and enriched team IDs.

        Raises:
            ValidationError: If ``series_id`` or ``game_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> data = vlrdevapi.series.rounds(series_id=12345, game_id=1)
            >>> len(data.rounds)
            24
            >>> data.rounds[0].winning_team
            'Team1'

        """
        html = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=overview")
        result = parse_rounds_data(html)
        result.series_id = series_id
        result.game_id = game_id

        html_series = self._sync._fetch(series_path(series_id))
        return _enrich_rounds(result, html_series)



def _enrich_rounds(result: RoundsData, html_series: HTMLParser) -> RoundsData:
    """Enrich round data with team IDs from the series info.

    Args:
        result: The RoundsData to enrich.
        html_series: HTML of the series page for team info parsing.

    Returns:
        RoundsData: Enriched round data with team IDs.

    """
    series_info = parse_series_info(html_series)
    if series_info.team1 and series_info.team1.tag == result.team1:
        result.team1_id = series_info.team1.id
    if series_info.team2 and series_info.team2.tag == result.team2:
        result.team2_id = series_info.team2.id

    for round_data in result.rounds:
        if round_data.winner_team_name == result.team1:
            round_data.winner_team_id = result.team1_id
        else:
            round_data.winner_team_id = result.team2_id

    return result
