"""Player agents namespace."""

from typing import Literal

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._player.agents.models import AgentStatsPage
from vlrdevapi._player.agents.parser import parse_agent_stats
from vlrdevapi.exceptions import ValidationError
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate

_VALID_TIMESPANS = ("30d", "60d", "90d", "all")


class AgentsNamespace:
    """Access per-agent statistics for a player from vlr.gg."""

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
    def __call__(self, player_id: int, timespan: Literal["30d", "60d", "90d", "all"] = "all") -> AgentStatsPage:
        """Get per-agent statistics for a player.

        Args:
            player_id: The unique player identifier on vlr.gg.
            timespan: Time period filter. One of ``30d``, ``60d``, ``90d``, ``all``.
                Defaults to ``all``.

        Returns:
            AgentStatsPage: An object with ``agents`` (list of
            ``AgentStats``, each with ``name``, ``rounds``, ``wins``,
            ``rating``, ``acs``, ``kd``, and ``adr``) and ``timespan``.

        Raises:
            ValidationError: If ``player_id`` is not a valid positive integer
                or if ``timespan`` is not one of the allowed values.
            NotFoundError: If the player page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.player.agents(player_id=11225, timespan="60d")
            >>> result.agents[0].name
            'Raze'
            >>> result.agents[0].rating
            1.19

        """
        _validate_timespan(timespan)
        path = _build_path(player_id, timespan)
        html = self._sync._fetch(path)
        return parse_agent_stats(html, timespan)


def _validate_timespan(timespan: str) -> None:
    if timespan not in _VALID_TIMESPANS:
        msg = f"invalid timespan '{timespan}', must be one of {_VALID_TIMESPANS}"
        raise ValidationError(
            msg,
        )


def _build_path(player_id: int, timespan: str) -> str:
    return f"/player/{player_id}/?timespan={timespan}"
