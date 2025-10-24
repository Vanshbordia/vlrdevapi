"""Centralized HTTP fetcher with retry logic and error handling."""

from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import httpx

from .config import get_config
from .exceptions import NetworkError, RateLimitError


_config = get_config()

_DEFAULT_HEADERS = {
    "User-Agent": _config.default_user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "utf-8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
}

_sync_client_lock = threading.Lock()
_sync_client: Optional[httpx.Client] = None
_sync_client_http1: Optional[httpx.Client] = None

_async_client: Optional[httpx.AsyncClient] = None
_async_client_http1: Optional[httpx.AsyncClient] = None
_async_client_lock: Optional[asyncio.Lock] = None

_cache_lock = threading.Lock()

# Thread pool for concurrent fetching
_thread_pool: Optional[ThreadPoolExecutor] = None
_thread_pool_lock = threading.Lock()
DEFAULT_MAX_WORKERS = 4  # Default number of concurrent workers

# Rate limiting configuration
_rate_limit_enabled = bool(_config.default_rate_limit_enabled)
_rate_limit_requests_per_second = float(_config.default_rate_limit)
_rate_limit_lock = threading.Lock()
_rate_limit_async_lock: Optional[asyncio.Lock] = None


class RateLimiter:
    """
    Token bucket rate limiter for controlling request frequency.
    
    Thread-safe implementation that works for both sync and async contexts.
    Uses a sliding window approach to track requests per second.
    """
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0.0
        self.lock = threading.Lock()
    
    def acquire(self) -> None:
        """Wait if necessary to respect rate limit (synchronous)."""
        if self.requests_per_second <= 0:
            return
        
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
                self.last_request_time = time.time()
            else:
                self.last_request_time = now
    
    async def acquire_async(self) -> None:
        """Wait if necessary to respect rate limit (asynchronous)."""
        if self.requests_per_second <= 0:
            return
        
        # Use asyncio-compatible timing
        now = time.time()
        
        # We need to be careful with async locking
        with self.lock:
            time_since_last = now - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
            else:
                sleep_time = 0
                self.last_request_time = now
        
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
            with self.lock:
                self.last_request_time = time.time()


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None
_rate_limiter_lock = threading.Lock()


def _get_rate_limiter() -> Optional[RateLimiter]:
    """Get or create the global rate limiter."""
    global _rate_limiter
    
    if not _rate_limit_enabled:
        return None
    
    if _rate_limiter is None:
        with _rate_limiter_lock:
            if _rate_limiter is None:
                _rate_limiter = RateLimiter(_rate_limit_requests_per_second)
    
    return _rate_limiter


def configure_rate_limit(requests_per_second: Optional[float] = None, enabled: Optional[bool] = None) -> None:
    """
    Configure the global rate limiter settings.
    
    Args:
        requests_per_second: Maximum requests per second (default: 10).
                           Set to 0 or None to disable rate limiting.
        enabled: Whether rate limiting is enabled (default: True).
    
    Example:
        >>> import vlrdevapi as vlr
        >>> # Set to 5 requests per second
        >>> vlr.configure_rate_limit(requests_per_second=5)
        >>> 
        >>> # Disable rate limiting
        >>> vlr.configure_rate_limit(enabled=False)
        >>> 
        >>> # Re-enable with custom rate
        >>> vlr.configure_rate_limit(requests_per_second=20, enabled=True)
    """
    global _rate_limit_enabled, _rate_limit_requests_per_second, _rate_limiter
    
    with _rate_limiter_lock:
        if enabled is not None:
            _rate_limit_enabled = enabled
        
        if requests_per_second is not None:
            _rate_limit_requests_per_second = float(requests_per_second)
        
        # Reset the rate limiter to apply new settings
        _rate_limiter = None


def _build_headers(user_agent: str) -> dict[str, str]:
    headers = _DEFAULT_HEADERS.copy()
    if user_agent and user_agent != headers["User-Agent"]:
        headers["User-Agent"] = user_agent
    return headers


def _compute_timeout(timeout: float) -> httpx.Timeout:
    timeout_value = timeout if timeout is not None else _config.default_timeout
    return httpx.Timeout(timeout_value)


def _get_sync_client(use_http1: bool = False) -> httpx.Client:
    """Get or create a shared synchronous HTTP client with connection pooling."""
    global _sync_client, _sync_client_http1
    
    if use_http1:
        if _sync_client_http1 is None:
            with _sync_client_lock:
                if _sync_client_http1 is None:
                    _sync_client_http1 = httpx.Client(
                        http2=False,
                        headers=_DEFAULT_HEADERS.copy(),
                        timeout=httpx.Timeout(_config.default_timeout),
                        follow_redirects=True,
                        limits=httpx.Limits(
                            max_connections=100,
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0,
                        ),
                    )
        return _sync_client_http1
    else:
        if _sync_client is None:
            with _sync_client_lock:
                if _sync_client is None:
                    _sync_client = httpx.Client(
                        http2=True,
                        headers=_DEFAULT_HEADERS.copy(),
                        timeout=httpx.Timeout(_config.default_timeout),
                        follow_redirects=True,
                        limits=httpx.Limits(
                            max_connections=100,
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0,
                        ),
                    )
        return _sync_client


async def _get_async_client(use_http1: bool = False) -> httpx.AsyncClient:
    """Get or create a shared asynchronous HTTP client with connection pooling."""
    global _async_client, _async_client_http1
    global _async_client_lock
    
    if use_http1:
        if _async_client_http1 is None:
            if _async_client_lock is None:
                _async_client_lock = asyncio.Lock()
            async with _async_client_lock:
                if _async_client_http1 is None:
                    _async_client_http1 = httpx.AsyncClient(
                        http2=False,
                        headers=_DEFAULT_HEADERS.copy(),
                        timeout=httpx.Timeout(_config.default_timeout),
                        follow_redirects=True,
                        limits=httpx.Limits(
                            max_connections=100,
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0,
                        ),
                    )
        return _async_client_http1
    else:
        if _async_client is None:
            if _async_client_lock is None:
                _async_client_lock = asyncio.Lock()
            async with _async_client_lock:
                if _async_client is None:
                    _async_client = httpx.AsyncClient(
                        http2=True,
                        headers=_DEFAULT_HEADERS.copy(),
                        timeout=httpx.Timeout(_config.default_timeout),
                        follow_redirects=True,
                        limits=httpx.Limits(
                            max_connections=100,
                            max_keepalive_connections=20,
                            keepalive_expiry=30.0,
                        ),
                    )
        return _async_client


def fetch_html_with_retry(
    url: str,
    timeout: float | None = None,
    max_retries: int | None = None,
    backoff_factor: float | None = None,
    user_agent: str | None = None,
) -> str:
    """
    Fetch HTML with retry logic, connection pooling, rate limiting, and exponential backoff.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries.
        backoff_factor: Backoff multiplier for delays.
        user_agent: User-Agent header.

    Returns:
        HTML content as string.

    Raises:
        NetworkError: On network failures.
        RateLimitError: On 429 responses.
    """
    # Apply rate limiting before making the request
    rate_limiter = _get_rate_limiter()
    if rate_limiter:
        rate_limiter.acquire()
    
    # Resolve dynamic defaults
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    effective_retries = int(max_retries if max_retries is not None else _config.max_retries)
    effective_backoff = float(backoff_factor if backoff_factor is not None else _config.backoff_factor)
    effective_ua = user_agent if user_agent is not None else _config.default_user_agent

    headers = _build_headers(effective_ua)
    request_timeout = _compute_timeout(effective_timeout)
    last_exception: Optional[Exception] = None
    http2_failed = False

    for attempt in range(effective_retries + 1):
        # Use HTTP/1.1 if HTTP/2 previously failed
        client = _get_sync_client(use_http1=http2_failed)
        
        try:
            response = client.get(url, headers=headers, timeout=request_timeout)
        except httpx.TimeoutException as exc:
            last_exception = exc
        except httpx.HTTPError as exc:
            # If HTTP/2 fails with protocol error, try HTTP/1.1
            if not http2_failed and "http2" in str(exc).lower():
                http2_failed = True
                continue
            last_exception = exc
        else:
            status = response.status_code
            if status == 429:
                raise RateLimitError("Rate limited", url=url, status_code=429)
            if status >= 500:
                last_exception = NetworkError("Server error", url=url, status_code=status)
            elif status >= 400:
                raise NetworkError("Client error", url=url, status_code=status)
            else:
                # Force UTF-8 decoding to ensure consistent unicode behavior
                try:
                    response.encoding = "utf-8"
                except Exception:
                    pass
                return response.text

        if attempt < effective_retries and last_exception is not None:
            delay = effective_backoff * (2 ** attempt)
            time.sleep(delay)
        else:
            break

    if last_exception is None:
        raise NetworkError(
            f"Failed to fetch after {effective_retries} retries",
            url=url,
            context={"max_retries": effective_retries},
        )
    if isinstance(last_exception, NetworkError):
        raise last_exception
    raise NetworkError(f"Failed to fetch: {last_exception}", url=url, context={"cause": str(last_exception)}) from last_exception


async def fetch_html_with_retry_async(
    url: str,
    timeout: float | None = None,
    max_retries: int | None = None,
    backoff_factor: float | None = None,
    user_agent: str | None = None,
) -> str:
    """Async counterpart to `fetch_html_with_retry` using shared async client."""

    # Apply rate limiting before making the request
    rate_limiter = _get_rate_limiter()
    if rate_limiter:
        await rate_limiter.acquire_async()

    # Resolve dynamic defaults
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    effective_retries = int(max_retries if max_retries is not None else _config.max_retries)
    effective_backoff = float(backoff_factor if backoff_factor is not None else _config.backoff_factor)
    effective_ua = user_agent if user_agent is not None else _config.default_user_agent

    headers = _build_headers(effective_ua)
    request_timeout = _compute_timeout(effective_timeout)
    last_exception: Optional[Exception] = None
    http2_failed = False

    for attempt in range(effective_retries + 1):
        # Use HTTP/1.1 if HTTP/2 previously failed
        client = await _get_async_client(use_http1=http2_failed)
        
        try:
            response = await client.get(url, headers=headers, timeout=request_timeout)
        except httpx.TimeoutException as exc:
            last_exception = exc
        except httpx.HTTPError as exc:
            # If HTTP/2 fails with protocol error, try HTTP/1.1
            if not http2_failed and "http2" in str(exc).lower():
                http2_failed = True
                continue
            last_exception = exc
        else:
            status = response.status_code
            if status == 429:
                raise RateLimitError("Rate limited", url=url, status_code=429)
            if status >= 500:
                last_exception = NetworkError("Server error", url=url, status_code=status)
            elif status >= 400:
                raise NetworkError("Client error", url=url, status_code=status)
            else:
                try:
                    response.encoding = "utf-8"
                except Exception:
                    pass
                return response.text

        if attempt < effective_retries and last_exception is not None:
            delay = effective_backoff * (2 ** attempt)
            await asyncio.sleep(delay)
        else:
            break

    if last_exception is None:
        raise NetworkError(
            f"Failed to fetch after {effective_retries} retries",
            url=url,
            context={"max_retries": effective_retries},
        )
    if isinstance(last_exception, NetworkError):
        raise last_exception
    raise NetworkError(f"Failed to fetch: {last_exception}", url=url, context={"cause": str(last_exception)}) from last_exception


# Cache for HTML to avoid redundant fetches in tests/same session
_HTML_CACHE: dict[str, str] = {}


def fetch_html(url: str, timeout: float | None = None, use_cache: bool = True) -> str:
    """
    Public interface for fetching HTML with caching and retries.

    Args:
        url: URL to fetch.
        timeout: Timeout in seconds.
        use_cache: Whether to use in-memory cache.

    Returns:
        HTML string.
    """
    if use_cache:
        with _cache_lock:
            cached = _HTML_CACHE.get(url)
        if cached is not None:
            return cached
    html = fetch_html_with_retry(url, timeout=timeout)
    if use_cache:
        with _cache_lock:
            _HTML_CACHE[url] = html
    return html


async def fetch_html_async(
    url: str,
    timeout: float | None = None,
    use_cache: bool = True,
) -> str:
    """Async convenience helper mirroring `fetch_html`."""

    if use_cache:
        with _cache_lock:
            cached = _HTML_CACHE.get(url)
        if cached is not None:
            return cached
    html = await fetch_html_with_retry_async(url, timeout=timeout)
    if use_cache:
        with _cache_lock:
            _HTML_CACHE[url] = html
    return html


def _get_thread_pool(max_workers: int = DEFAULT_MAX_WORKERS) -> ThreadPoolExecutor:
    """Get or create a shared thread pool for concurrent fetching."""
    global _thread_pool
    if _thread_pool is None:
        with _thread_pool_lock:
            if _thread_pool is None:
                _thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    return _thread_pool


def batch_fetch_html(
    urls: list[str],
    timeout: float | None = None,
    use_cache: bool = True,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> dict[str, str | Exception]:
    """
    Fetch multiple URLs concurrently using threading with request deduplication.
    
    This function allows fetching 2-4+ pages simultaneously while keeping
    the API synchronous. Perfect for scenarios where you need to fetch
    multiple pages to get complete data.
    
    Duplicate URLs in the input list are automatically deduplicated to avoid
    redundant network requests.
    
    Args:
        urls: List of URLs to fetch (duplicates will be deduplicated).
        timeout: Request timeout in seconds.
        use_cache: Whether to use in-memory cache.
        max_workers: Maximum number of concurrent threads (default: 4).
    
    Returns:
        Dictionary mapping URLs to their HTML content or Exception if failed.
        
    Example:
        >>> urls = ["https://example.com/page1", "https://example.com/page2"]
        >>> results = batch_fetch_html(urls, max_workers=4)
        >>> for url, content in results.items():
        ...     if isinstance(content, Exception):
        ...         print(f"Failed to fetch {url}: {content}")
        ...     else:
        ...         print(f"Fetched {url}: {len(content)} bytes")
    """
    if not urls:
        return {}
    
    # Deduplicate URLs to avoid redundant requests
    unique_urls = list(dict.fromkeys(urls))  # Preserves order
    
    results: dict[str, str | Exception] = {}
    urls_to_fetch: list[str] = []
    
    # Check cache first
    if use_cache:
        with _cache_lock:
            for url in unique_urls:
                cached = _HTML_CACHE.get(url)
                if cached is not None:
                    results[url] = cached
                else:
                    urls_to_fetch.append(url)
    else:
        urls_to_fetch = unique_urls.copy()
    
    # Fetch remaining URLs concurrently
    if urls_to_fetch:
        pool = _get_thread_pool(max_workers)
        
        # Submit all fetch tasks (already deduplicated)
        future_to_url = {
            pool.submit(fetch_html_with_retry, url, timeout): url
            for url in urls_to_fetch
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                html = future.result()
                results[url] = html
                # Cache successful results
                if use_cache:
                    with _cache_lock:
                        _HTML_CACHE[url] = html
            except Exception as exc:
                results[url] = exc
    
    return results




def get_rate_limit() -> float:
    """Get the current requests-per-second limit.
    
    Returns:
        float: Current RPS limit. Returns 0.0 when rate limiting is disabled.
    """
    # When disabled, report 0.0 for clarity
    return _rate_limit_requests_per_second if _rate_limit_enabled else 0.0


def reset_rate_limit() -> None:
    configure_rate_limit(
        requests_per_second=float(_config.default_rate_limit),
        enabled=bool(_config.default_rate_limit_enabled),
    )


def clear_cache() -> None:
    """Clear the HTML cache."""
    with _cache_lock:
        _HTML_CACHE.clear()


def close_connections() -> None:
    """Close all pooled connections and thread pool."""
    global _sync_client
    global _async_client
    global _thread_pool
    
    # Close sync client
    if _sync_client is not None:
        try:
            _sync_client.close()
        finally:
            _sync_client = None
    
    # Close thread pool
    if _thread_pool is not None:
        try:
            _thread_pool.shutdown(wait=True)
        finally:
            _thread_pool = None

    # Close async client
    async_client = _async_client
    _async_client = None
    if async_client is not None:
        if async_client.is_closed:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(async_client.aclose())
        else:
            loop.create_task(async_client.aclose())


async def aclose_connections() -> None:
    """Async helper to close shared async client explicitly."""

    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None
