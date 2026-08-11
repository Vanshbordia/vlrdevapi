"""News article namespace."""

from datetime import tzinfo
from zoneinfo import ZoneInfo

import httpx

from vlrdevapi._base import SyncNamespace
from vlrdevapi._news.article.models import NewsArticle
from vlrdevapi._news.article.parser import parse_news_article
from vlrdevapi._utils.paths import news_article
from vlrdevapi.exceptions import NotFoundError
from vlrdevapi.fetcher import (
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
)
from vlrdevapi.validators import sanitize_and_validate


class NewsArticleNamespace:
    """Access individual news articles from vlr.gg.

    Call the instance with an article ID to fetch the full article::

        article = vlrdevapi.news.article(734100)
        print(article.title)

    The namespace is reachable via ``vlrdevapi.news.article``. There is
    no need to instantiate it directly.
    """

    __slots__ = ("_source_tz", "_sync")

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
        self._sync = SyncNamespace(
            client, timeout, retry_config, rate_limiter, extra_headers
        )

    @sanitize_and_validate
    def __call__(self, article_id: int) -> NewsArticle:
        """Get a single news article from vlr.gg.

        Args:
            article_id: The news article ID. Use the ``id`` field of a
                ``News`` item from a listing, or the numeric prefix of
                its ``link``.

        Returns:
            NewsArticle: The article with ``title``, ``author``, ``date``,
                ``event_name``, ``event_link``, ``content`` (plain text),
                and ``content_md`` (Markdown).

        Raises:
            ValidationError: If ``article_id`` is not a valid positive integer.
            NotFoundError: If the article does not exist. vlr.gg returns a
                generic page (HTTP 200) for unknown article IDs, so this
                is detected from the page content.
            RequestError: If the HTTP request fails.
            RateLimitError: If the rate limit is exceeded.

        Examples:
            >>> article = vlrdevapi.news.article(734100)
            >>> article.title
            'Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins'
            >>> article.content_md.startswith('The [Pacific Stage 2]')
            True

        """
        html = self._sync._fetch(news_article(article_id))
        article = parse_news_article(html, source_tz=self._source_tz)
        if article.id == 0:
            raise NotFoundError(
                f"News article {article_id} not found (page contains no article content)."
            )
        return article
