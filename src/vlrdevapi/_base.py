"""Base class for sync namespaces with parallel fetch helpers."""

import concurrent.futures
import threading
from collections.abc import Callable
from typing import Any

import httpx
from selectolax.parser import HTMLParser

from vlrdevapi.fetcher import (
    BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT,
    RateLimiter,
    RetryConfig,
    fetch_sync,
)


class SyncNamespace:
    """Base class for synchronous namespaces."""

    __slots__ = ("_client", "_extra_headers", "_rate_limiter", "_retry_config", "_timeout")

    def __init__(
        self,
        client: httpx.Client,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
        rate_limiter: RateLimiter | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the namespace with shared client and request settings.

        Args:
            client: The ``httpx.Client`` used for HTTP requests.
            timeout: Request timeout in seconds. Defaults to ``DEFAULT_TIMEOUT``.
            retry_config: Configuration for retry behavior. Defaults to
                ``DEFAULT_RETRY_CONFIG``.
            rate_limiter: Optional rate limiter to throttle requests.
            extra_headers: Extra headers to merge into parallel fetch clients.

        """
        self._client = client
        self._timeout = timeout
        self._retry_config = retry_config
        self._rate_limiter = rate_limiter
        self._extra_headers = extra_headers

    def _fetch(self, path: str) -> HTMLParser:
        """Fetch a path relative to the base URL and return the parsed HTML.

        Args:
            path: URL path to append to the base URL.

        Returns:
            HTMLParser: Parsed HTML document from the response.

        """
        return fetch_sync(
            self._client,
            path,
            self._timeout,
            retry_config=self._retry_config,
            rate_limiter=self._rate_limiter,
        )

    def _make_client(self) -> httpx.Client:
        """Create a fresh ``httpx.Client`` for use in parallel worker threads.

        Returns:
            httpx.Client: A new client instance configured with the base URL,
                default headers, and redirect following enabled.

        """
        headers = {**DEFAULT_HEADERS, **(self._extra_headers or {})}
        return httpx.Client(
            base_url=BASE_URL,
            headers=headers,
            follow_redirects=True,
            verify=False,
        )

    def _parallel_fetch(
        self,
        paths: list[str],
        max_workers: int = 5,
    ) -> list[HTMLParser]:
        """Fetch multiple paths in parallel using a thread pool.

        Each worker thread creates its own ``httpx.Client`` since clients
        are not thread-safe.

        Args:
            paths: List of URL paths to fetch.
            max_workers: Maximum number of parallel worker threads. Defaults to
                ``5``.

        Returns:
            list[HTMLParser]: Parsed HTML documents for each successfully
                fetched path.

        """
        results: list[HTMLParser | None] = [None] * len(paths)

        def _do_fetch(idx: int, path: str) -> tuple[int, HTMLParser]:
            with self._make_client() as client:
                return idx, fetch_sync(
                    client, path, self._timeout,
                    retry_config=self._retry_config,
                    rate_limiter=self._rate_limiter,
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            for idx, html in pool.map(lambda x: _do_fetch(*x), enumerate(paths)):
                results[idx] = html

        return [r for r in results if r is not None]

    _thread_local = threading.local()

    def _parallel_enrich(
        self,
        items: list[Any],
        enrich_fn: Callable[[Any, httpx.Client], None],
        max_workers: int = 5,
    ) -> None:
        """Run an enrichment function on each item in parallel.

        Each worker thread gets its own ``httpx.Client`` via
        thread-local storage.

        Args:
            items: List of items to enrich.
            enrich_fn: Callable with signature ``fn(item, thread_client)``.
            max_workers: Maximum number of parallel worker threads. Defaults to
                ``5``.

        """
        def _init_worker() -> None:
            SyncNamespace._thread_local.client = self._make_client()

        def _work(item: Any) -> None:
            enrich_fn(item, SyncNamespace._thread_local.client)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, initializer=_init_worker,
        ) as pool:
            pool.map(_work, items)
