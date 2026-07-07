"""Series economy namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx
from selectolax.parser import HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series.economy.models import EconomyData
from vlrdevapi._series.economy.parser import parse_economy_data
from vlrdevapi._series.info.parser import parse_series_info
from vlrdevapi._utils.paths import series as series_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class SeriesEconomyNamespace:
    """Access economy data for a series game from vlr.gg."""

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
    def __call__(self, series_id: int, game_id: int) -> EconomyData:
        """Get economy data for a series game on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The unique game/map identifier on vlr.gg.

        Returns:
            EconomyData: Economy data including ``rounds`` (list of
            ``EconomyRound`` with purchases, remaining credits, and
            team spending per round), ``team1`` and ``team2`` names,
            and enriched team IDs.

        Raises:
            ValidationError: If ``series_id`` or ``game_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> econ = vlrdevapi.series.economy(series_id=12345, game_id=1)
            >>> econ.rounds[0].team1_creds
            24000
            >>> econ.rounds[0].winner.name
            'FNATIC'

        """
        html = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=economy")
        result = parse_economy_data(html)
        result.series_id = series_id
        result.game_id = game_id

        html_series = self._sync._fetch(series_path(series_id))
        return _enrich_economy(result, html_series)



def _enrich_economy(result: EconomyData, html_series: HTMLParser) -> EconomyData:
    """Enrich economy data with team IDs from the series info.

    Args:
        result: The EconomyData to enrich.
        html_series: HTML of the series page for team info parsing.

    Returns:
        EconomyData: Enriched economy data with team IDs.

    """
    series_info = parse_series_info(html_series)
    if series_info.team1 and series_info.team1.tag == result.team1:
        result.team1_id = series_info.team1.id
    if series_info.team2 and series_info.team2.tag == result.team2:
        result.team2_id = series_info.team2.id

    for round_data in result.rounds:
        temp_winner = getattr(round_data, "_temp_winner", "")
        if temp_winner == "team1":
            round_data.winner.name = result.team1
            round_data.winner.id = result.team1_id
        elif temp_winner == "team2":
            round_data.winner.name = result.team2
            round_data.winner.id = result.team2_id
        if hasattr(round_data, "_temp_winner"):
            delattr(round_data, "_temp_winner")

    return result
