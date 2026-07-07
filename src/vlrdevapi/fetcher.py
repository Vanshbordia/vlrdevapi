"""HTTP fetching layer with retry logic and rate limiting."""

import logging
import random
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Never

__all__ = [
    "BASE_URL",
    "DEFAULT_HEADERS",
    "DEFAULT_RATE_LIMIT",
    "DEFAULT_RETRY_CONFIG",
    "DEFAULT_TIMEOUT",
    "BackoffStrategy",
    "RateLimiter",
    "RetryConfig",
    "fetch_sync",
]

import httpx
from selectolax.parser import HTMLParser

from vlrdevapi.exceptions import HTTPError, NotFoundError, RateLimitError, RequestError

BASE_URL = "https://www.vlr.gg"
DEFAULT_TIMEOUT = 15
DEFAULT_RATE_LIMIT = 3.0
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.7",
    "Sec-Ch-Ua": '"Google Chrome";v="149", "Not(A:Brand";v="99", "Chromium";v="149"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}


logger = logging.getLogger(__name__)


class BackoffStrategy(str, Enum):
    """Backoff strategy for retry delays between attempts.

    Attributes:
        EXPONENTIAL: Delay doubles each attempt (``base_delay * 2^attempt``).
            e.g. 1s, 2s, 4s for ``base_delay=1``.
        LINEAR: Delay increases linearly (``base_delay * (attempt + 1)``).
            e.g. 1s, 2s, 3s for ``base_delay=1``.
        CONSTANT: Delay stays the same (``base_delay``).
            e.g. 1s, 1s, 1s for ``base_delay=1``.

    """

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"


@dataclass
class RetryConfig:
    """Configuration for HTTP request retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts after the initial request.
            Defaults to ``3`` (4 total attempts).
        base_delay: Base delay in seconds between retries. The actual delay
            depends on the backoff strategy. Defaults to ``1.0``.
        backoff: The backoff strategy used to calculate delay between retries.
            Defaults to ``BackoffStrategy.EXPONENTIAL``.

    """

    max_retries: int = 3
    base_delay: float = 1.0
    backoff: BackoffStrategy = BackoffStrategy.EXPONENTIAL


DEFAULT_RETRY_CONFIG = RetryConfig()


class RateLimiter:
    """Simple token-bucket rate limiter (thread-safe).

    Enforces a minimum interval between requests. Set *requests_per_second*
    to ``0`` (the default) to disable rate limiting entirely.

    Args:
        requests_per_second: Maximum average throughput. ``0`` means unlimited.

    """

    __slots__ = ("_last_request_time", "_lock", "_min_interval")

    def __init__(self, requests_per_second: float = 0) -> None:
        self._min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0.0
        self._last_request_time = 0.0
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        """Whether rate limiting is active (``True`` when a positive rate is configured).

        Returns:
            bool: ``True`` if rate limiting is enabled, ``False`` otherwise.

        """
        return self._min_interval > 0

    def acquire(self) -> None:
        """Block until the next request is allowed (sync)."""
        if not self.enabled:
            return
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request_time = time.monotonic()

def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    if isinstance(exc, httpx.HTTPError):
        return False
    return False


def _calc_delay(attempt: int, config: RetryConfig) -> float:
    if config.backoff == BackoffStrategy.EXPONENTIAL:
        delay = config.base_delay * (2**attempt)
    elif config.backoff == BackoffStrategy.LINEAR:
        delay = config.base_delay * (attempt + 1)
    else:
        delay = config.base_delay
    return delay * random.uniform(0.75, 1.25)


def _parse_response(response: httpx.Response) -> HTMLParser:
    return HTMLParser(response.text)


def _raise_mapped_exception(exc: Exception) -> Never:
    """Map an ``httpx`` exception to the corresponding ``vlrdevapi`` exception.

    Args:
        exc: The exception to map.

    Raises:
        NotFoundError: If the response status code is 404.
        RateLimitError: If the response status code is 429.
        HTTPError: For other non-2xx HTTP status codes.
        RequestError: For network or unexpected errors.

    """
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 404:
            raise NotFoundError from exc
        if status == 429:
            raise RateLimitError from exc
        msg = f"HTTP error {status}"
        raise HTTPError(msg, status) from exc
    if isinstance(exc, httpx.RequestError):
        msg = f"request failed: {exc}"
        raise RequestError(msg) from exc
    msg = f"unexpected error: {exc}"
    raise RequestError(msg) from exc


def fetch_sync(
    client: httpx.Client,
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
    rate_limiter: RateLimiter | None = None,
    headers: dict[str, str] | None = None,
) -> HTMLParser:
    """Fetch a URL synchronously with retry and rate-limiting support.

    Args:
        client: The ``httpx.Client`` to use for the request.
        url: The full URL to fetch.
        timeout: Request timeout in seconds. Defaults to ``DEFAULT_TIMEOUT``.
        retry_config: Configuration for retry behavior. Defaults to
            ``DEFAULT_RETRY_CONFIG``.
        rate_limiter: Optional rate limiter to throttle requests.
        headers: Optional additional HTTP headers for the request.

    Returns:
        HTMLParser: Parsed HTML of the response.

    Raises:
        NotFoundError: If the response status code is 404.
        RateLimitError: If the response status code is 429.
        HTTPError: For other non-2xx HTTP status codes.
        RequestError: For network or unexpected errors.

    """
    last_exc: Exception = RuntimeError("unreachable")
    for attempt in range(retry_config.max_retries + 1):
        try:
            if rate_limiter is not None:
                rate_limiter.acquire()
            resp = client.get(url, timeout=timeout, headers=headers)
            resp.raise_for_status()
            return _parse_response(resp)
        except Exception as exc:  # noqa: BLE001
            if not _is_retryable(exc):
                _raise_mapped_exception(exc)
            last_exc = exc
            if attempt < retry_config.max_retries:
                delay = _calc_delay(attempt, retry_config)
                logger.warning(
                    "Retry %d/%d for %s after %.1fs: %s",
                    attempt + 1,
                    retry_config.max_retries,
                    url,
                    delay,
                    exc,
                )
                time.sleep(delay)
    _raise_mapped_exception(last_exc)



