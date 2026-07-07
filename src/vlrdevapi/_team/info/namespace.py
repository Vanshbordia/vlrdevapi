"""Team info namespace — fetches light and dark mode HTML for logo extraction."""

import httpx
from selectolax.parser import HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._team.info.models import TeamInfo
from vlrdevapi._team.info.parser import parse_team_info
from vlrdevapi._utils.paths import team as team_path
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
    fetch_sync,
)
from vlrdevapi.validators import sanitize_and_validate

# Cookie header for dark mode — avoids httpx per-request cookies deprecation
_DARK_MODE_COOKIE_HEADER = {"Cookie": "settings=%7B%22dark_mode%22%3A1%7D"}


class TeamInfoNamespace:
    """Access team info from vlr.gg."""

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        self._sync = SyncNamespace(client, timeout, retry_config, rate_limiter, extra_headers)

    def _sync_get(self, team_id: int) -> TeamInfo:
        """Fetch team info synchronously.

        Args:
            team_id: The unique team identifier on vlr.gg.

        Returns:
            TeamInfo: Team details for the given team.

        """
        return self(team_id)

    @sanitize_and_validate
    def __call__(self, team_id: int) -> TeamInfo:
        """Get info for a team on vlr.gg.

        Args:
            team_id: The unique team identifier on vlr.gg.

        Returns:
            TeamInfo: Team details including ``name``, ``tag``, ``country``,
            ``logo_url``, and social media links (``twitter``, ``twitch``,
            ``youtube``).

        Raises:
            ValidationError: If ``team_id`` is not a valid positive integer.
            NotFoundError: If the team page does not exist (HTTP 404).
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.
            ParsingError: If the page structure is unrecognised.

        Examples:
            >>> result = vlrdevapi.team.info(team_id=4568)
            >>> result.name
            'Sentinels'
            >>> result.tag
            'SEN'

        """
        path = team_path(team_id)

        light_html_tree = self._sync._fetch(path)
        light_html = str(light_html_tree.html)

        dark_html_tree = fetch_sync(
            self._sync._client, path, self._sync._timeout,
            retry_config=self._sync._retry_config, rate_limiter=self._sync._rate_limiter,
            headers=_DARK_MODE_COOKIE_HEADER,
        )
        dark_html = str(dark_html_tree.html)

        light_parsed = HTMLParser(light_html)
        dark_parsed = HTMLParser(dark_html)
        result = parse_team_info(light_parsed, dark_parsed)
        result.id = team_id
        return result

