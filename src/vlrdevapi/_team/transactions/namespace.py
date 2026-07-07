"""Team transactions namespace."""

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._team.transactions.models import TeamTransactions
from vlrdevapi._team.transactions.parser import parse_team_transactions
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class TeamTransactionsNamespace:
    """Access team transactions from vlr.gg."""

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
    def __call__(self, team_id: int) -> TeamTransactions:
        """Get roster transactions (joins/leaves) for a team.

        Args:
            team_id: The unique team identifier on vlr.gg.

        Returns:
            TeamTransactions: Chronological list of ``transactions`` including ``action`` (Join/Leave/Inactive), ``player`` details, ``date``, and ``position``.

        Raises:
            ValidationError: If ``team_id`` is not a valid positive integer.
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.team.transactions(team_id=4568)
            >>> result.transactions[0].action
            'Join'

        """
        html = self._sync._fetch(f"/team/transactions/{team_id}/")
        return parse_team_transactions(html, team_id)

