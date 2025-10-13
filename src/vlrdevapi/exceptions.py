"""Custom exceptions for vlrdevapi."""


class VlrdevapiError(Exception):
    """Base exception for vlrdevapi errors."""
    pass


class NetworkError(VlrdevapiError):
    """Raised when network requests fail."""
    pass


class ScrapingError(VlrdevapiError):
    """Raised when HTML parsing or scraping fails."""
    pass


class DataNotFoundError(VlrdevapiError):
    """Raised when expected data is not found on the page."""
    pass


class RateLimitError(VlrdevapiError):
    """Raised when rate limited by the server."""
    pass
