"""Centralized HTTP fetcher with retry logic and error handling."""

import time
from http.client import HTTPConnection, HTTPSConnection
from typing import Optional
from urllib import error, request, parse

from .constants import VLR_BASE, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT, MAX_RETRIES, BACKOFF_FACTOR
from .exceptions import NetworkError, RateLimitError

# Connection pool for keep-alive and reuse
_connection_pool: dict[str, HTTPSConnection | HTTPConnection] = {}


def _get_connection(host: str, use_https: bool = True) -> HTTPSConnection | HTTPConnection:
    """Get or create a persistent connection from the pool."""
    key = f"{host}:{use_https}"
    if key not in _connection_pool:
        if use_https:
            _connection_pool[key] = HTTPSConnection(host, timeout=DEFAULT_TIMEOUT)
        else:
            _connection_pool[key] = HTTPConnection(host, timeout=DEFAULT_TIMEOUT)
    return _connection_pool[key]


def fetch_html_with_retry(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = MAX_RETRIES,
    backoff_factor: float = BACKOFF_FACTOR,
    user_agent: str = DEFAULT_USER_AGENT,
) -> str:
    """
    Fetch HTML with retry logic, connection pooling, and exponential backoff.

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
    last_exception: Optional[Exception] = None
    parsed = parse.urlparse(url)
    host = parsed.netloc
    path = parsed.path or "/"
    if parsed.query:
        path += f"?{parsed.query}"
    use_https = parsed.scheme == "https"
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    for attempt in range(max_retries + 1):
        try:
            conn = _get_connection(host, use_https)
            conn.request("GET", path, headers=headers)
            resp = conn.getresponse()
            
            if resp.status == 429:
                raise RateLimitError(f"Rate limited on {url}")
            elif resp.status >= 500:
                # Retry on server errors
                last_exception = Exception(f"Server error {resp.status}")
                resp.read()  # Consume response
            elif resp.status >= 400:
                resp.read()  # Consume response
                raise NetworkError(f"HTTP {resp.status} on {url}")
            else:
                # Success
                data = resp.read()
                # Handle gzip encoding
                if resp.getheader("Content-Encoding") == "gzip":
                    import gzip
                    data = gzip.decompress(data)
                return data.decode("utf-8", errors="ignore")
        except RateLimitError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            # Network/connection errors - retry
            last_exception = e
            # Close bad connection
            key = f"{host}:{use_https}"
            if key in _connection_pool:
                try:
                    _connection_pool[key].close()
                except:
                    pass
                del _connection_pool[key]

        if attempt < max_retries and last_exception:
            delay = backoff_factor * (2 ** attempt)
            time.sleep(delay)
        elif last_exception:
            break

    if last_exception:
        raise NetworkError(f"Failed to fetch {url}: {last_exception}") from last_exception
    raise NetworkError(f"Failed to fetch {url} after {max_retries} retries")


# Cache for HTML to avoid redundant fetches in tests/same session
_HTML_CACHE: dict[str, str] = {}


def fetch_html(url: str, timeout: float = DEFAULT_TIMEOUT, use_cache: bool = True) -> str:
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
        cached = _HTML_CACHE.get(url)
        if cached is not None:
            return cached
    html = fetch_html_with_retry(url, timeout=timeout)
    if use_cache:
        _HTML_CACHE[url] = html
    return html


def clear_cache() -> None:
    """Clear the HTML cache."""
    _HTML_CACHE.clear()


def close_connections() -> None:
    """Close all pooled connections."""
    for conn in _connection_pool.values():
        try:
            conn.close()
        except:
            pass
    _connection_pool.clear()
