"""Top-level namespace exposing upcoming, live, and completed match sub-namespaces."""

import httpx

from vlrdevapi._matches.completed.namespace import CompletedMatchesNamespace
from vlrdevapi._matches.live.namespace import LiveMatchesNamespace
from vlrdevapi._matches.upcoming.namespace import UpcomingMatchesNamespace
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)


class MatchesNamespace:
    """Top-level namespace for match listings.

    Access sub-namespaces for upcoming, live, and completed matches.

    Example:
        >>> upcoming = vlrdevapi.matches.upcoming()
        >>> live = vlrdevapi.matches.live()
        >>> completed = vlrdevapi.matches.completed(page=1)

    """

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._upcoming = UpcomingMatchesNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._live = LiveMatchesNamespace(client, timeout, retry_config, rate_limiter, extra_headers)
        self._completed = CompletedMatchesNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    @property
    def upcoming(self) -> UpcomingMatchesNamespace:
        """Upcoming matches sub-namespace.

        Returns:
            UpcomingMatchesNamespace: Callable instance that fetches and
                returns an ``UpcomingMatchesPage`` model.

        """
        return self._upcoming

    @property
    def live(self) -> LiveMatchesNamespace:
        """Live matches sub-namespace.

        Returns:
            LiveMatchesNamespace: Callable instance that fetches and
                returns a ``LiveMatchesPage`` model.

        """
        return self._live

    @property
    def completed(self) -> CompletedMatchesNamespace:
        """Completed matches sub-namespace.

        Returns:
            CompletedMatchesNamespace: Callable instance that accepts
                optional ``page`` and ``date`` parameters and returns a
                ``CompletedMatchesPage`` model.

        """
        return self._completed



