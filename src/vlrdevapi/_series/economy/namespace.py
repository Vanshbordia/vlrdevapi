"""Series economy namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series._utils import _extract_team_abbreviations
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
    def __call__(self, series_id: int, game_id: int | str = "all") -> EconomyData:
        """Get economy data for a series game on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The game number within the series (1-based), a real
                VLR game ID, or "all" for combined series economy.

        Returns:
            EconomyData: Economy data including ``rounds`` (list of
            ``RoundEconomyData`` with purchases, remaining credits,
            spending, buy tier, and winner per round; the winning side
            comes from ``series.rounds``),
            ``buy_matrix_team1``/``buy_matrix_team2`` (the economy tab's
            pistol/conv/bonus summary and per-buy-tier records), the flat
            ``pistol_team1``/``converted_team1``/``bonus_team1`` and
            ``pistol_team2``/``converted_team2``/``bonus_team2``
            shortcuts, ``team1`` and ``team2`` names, and enriched team
            IDs.

        Raises:
            ValidationError: If ``series_id`` or ``game_id`` is not a valid
                positive integer.
            NotFoundError: If the series page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> econ = vlrdevapi.series.economy(series_id=12345, game_id=1)
            >>> econ.rounds[0].bank_team1
            24000.0
            >>> econ.rounds[0].winner.name
            'FNATIC'

        """
        html = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=economy")
        result = parse_economy_data(html, game_id=game_id)
        result.series_id = series_id
        result.game_id = game_id

        html_series = self._sync._fetch(series_path(series_id))
        return _enrich_economy(result, html_series)



def _enrich_economy(result: EconomyData, html_series: HTMLParser) -> EconomyData:
    """Enrich economy data with team IDs and round winners from the series info.

    Team matching compares the parsed economy team tag against both the
    abbreviation-level names extracted from ``.ovw-player-tag`` elements
    (e.g. "SEN") and the full team names from the series header, using a
    case-insensitive match.  Round winners are resolved from the stored
    ``_temp_winner`` tag set during parsing.

    Args:
        result: The EconomyData to enrich.
        html_series: HTML of the series page for team info parsing.

    Returns:
        EconomyData: Enriched economy data with team IDs and round winners.

    """
    series_info = parse_series_info(html_series)
    team1_abbr, team2_abbr = _extract_team_abbreviations(html_series)

    def _normalize(value: str) -> str:
        return (value or "").strip().casefold()

    team1_keys = {_normalize(team1_abbr), _normalize(series_info.team1.name)}
    team2_keys = {_normalize(team2_abbr), _normalize(series_info.team2.name)}

    if _normalize(result.team1) in team1_keys:
        result.team1_id = series_info.team1.id

    if _normalize(result.team2) in team2_keys:
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
