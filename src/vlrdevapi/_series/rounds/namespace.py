"""Series rounds namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._series._utils import _extract_team_abbreviations
from vlrdevapi._series.economy.models import BuyType
from vlrdevapi._series.economy.parser import parse_economy_data
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
        source_tz: ZoneInfo | tzinfo | None = None,
    ):
        self._source_tz = source_tz
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @sanitize_and_validate
    def __call__(self, series_id: int, game_id: int) -> RoundsData:
        """Get round-by-round data for a series game on vlr.gg.

        Args:
            series_id: The unique series identifier on vlr.gg.
            game_id: The game number within the series (1-based), or its
                real VLR game ID.

        Returns:
            RoundsData: Round-by-round data including ``rounds``
            (list of ``RoundData`` with win type, side, scores, plus the
            bank, spend, and buy types per team merged from the economy
            tab), ``team1`` and ``team2`` names, and enriched team IDs.

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
            >>> data.rounds[0].winner_team_name
            'Team1'

        """
        html = self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=overview")
        result = parse_rounds_data(html, game_id=game_id)
        result.series_id = series_id
        result.game_id = game_id

        html_series = self._sync._fetch(series_path(series_id))
        result = _enrich_rounds(result, html_series)

        def _fetch_economy() -> HTMLParser:
            return self._sync._fetch(f"{series_path(series_id)}?game={game_id}&tab=economy")

        return _enrich_rounds_with_economy(result, _fetch_economy)



def _enrich_rounds(result: RoundsData, html_series: HTMLParser) -> RoundsData:
    """Enrich round data with team IDs from the series info.

    Team matching first tries abbreviation-level names extracted from
    ``.ovw-player-tag`` elements (e.g. "SEN"), then falls back to full
    team names from the series header.

    Args:
        result: The RoundsData to enrich.
        html_series: HTML of the series page for team info parsing.

    Returns:
        RoundsData: Enriched round data with team IDs.

    """
    series_info = parse_series_info(html_series)
    team1_abbr, team2_abbr = _extract_team_abbreviations(html_series)

    if team1_abbr == result.team1 or result.team1 and series_info.team1.name == result.team1:
        result.team1_id = series_info.team1.id

    if team2_abbr == result.team2 or result.team2 and series_info.team2.name == result.team2:
        result.team2_id = series_info.team2.id

    for round_data in result.rounds:
        if round_data.winner_team_name == result.team1:
            round_data.winner_team_id = result.team1_id
        else:
            round_data.winner_team_id = result.team2_id

    return result


def _enrich_rounds_with_economy(result: RoundsData, fetch_economy) -> RoundsData:
    """Merge per-round economy data from the economy tab into the rounds.

    Bank, spend, and buy types come from the economy tab's round grid.
    The merge is skipped (leaving the economy fields ``None``/empty) when
    the economy page cannot be fetched or does not include this game.

    Args:
        result: The RoundsData to enrich.
        fetch_economy: Zero-argument callable returning the HTMLParser of
            the series' economy tab.

    Returns:
        RoundsData: Enriched round data.

    """
    if not result.rounds:
        return result

    try:
        html_economy = fetch_economy()
        economy = parse_economy_data(html_economy, game_id=result.game_id)
    except Exception:  # noqa: BLE001  - optional merge; degrade gracefully
        return result

    if not economy.rounds:
        return result

    # The economy grid lists team 1 first, same as the round strip, but
    # detect a swapped order when the tags clearly cross-match.
    swap = (
        bool(result.team1 and result.team2 and economy.team1 and economy.team2)
        and economy.team1.casefold() == result.team2.casefold()
        and economy.team2.casefold() == result.team1.casefold()
    )

    econ_by_round = {r.round_number: r for r in economy.rounds}
    for round_data in result.rounds:
        econ_round = econ_by_round.get(round_data.round_number)
        if econ_round is None:
            continue
        bank1, bank2 = (
            (econ_round.bank_team2, econ_round.bank_team1)
            if swap
            else (econ_round.bank_team1, econ_round.bank_team2)
        )
        spent1, spent2 = (
            (econ_round.spent_team2, econ_round.spent_team1)
            if swap
            else (econ_round.spent_team1, econ_round.spent_team2)
        )
        buy1, buy2 = (
            (econ_round.buy_type_team2, econ_round.buy_type_team1)
            if swap
            else (econ_round.buy_type_team1, econ_round.buy_type_team2)
        )
        round_data.bank_team1 = bank1
        round_data.bank_team2 = bank2
        round_data.spent_team1 = spent1
        round_data.spent_team2 = spent2
        round_data.buy_type_team1 = _buy_value(buy1)
        round_data.buy_type_team2 = _buy_value(buy2)

    return result


def _buy_value(value: object) -> str:
    """Normalize a buy type to its plain string value."""
    return value.value if isinstance(value, BuyType) else str(value)
