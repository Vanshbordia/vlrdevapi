"""Custom exceptions for vlrdevapi."""

from typing import Any, Optional


class VlrdevapiError(Exception):
    """Base exception for vlrdevapi errors.

    Args:
        message: Error message
        url: URL that caused the error (optional)
        status_code: HTTP status code if applicable (optional)
        context: Additional context information (optional)
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.context = context or {}

    def __str__(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.status_code is not None:
            parts.append(f"Status: {self.status_code}")
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"url={self.url!r}, "
            f"status_code={self.status_code!r}, "
            f"context={self.context!r})"
        )


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
