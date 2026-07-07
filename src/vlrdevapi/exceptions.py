"""Custom exceptions for the vlrdevapi library."""

__all__ = [
    "ClientError",
    "DataNotFoundError",
    "HTTPError",
    "NotFoundError",
    "ParseStructureError",
    "ParsingError",
    "RateLimitError",
    "RequestError",
    "RequestTimeoutError",
    "ServerError",
    "TimeoutError",
    "ValidationError",
    "VlrdevapiError",
    "VlrdevapiException",
]


class VlrdevapiError(Exception):
    """Base exception for all vlrdevapi errors."""


VlrdevapiException = VlrdevapiError


class RequestError(VlrdevapiError):
    """Raised when an HTTP request fails (network error, timeout, etc.)."""


class RequestTimeoutError(RequestError):
    """Raised when an HTTP request times out."""


TimeoutError = RequestTimeoutError


class HTTPError(VlrdevapiError):
    """Raised when an HTTP response has an error status code."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.args[0]!r}, status_code={self.status_code})"


class NotFoundError(HTTPError):
    """Raised when a requested resource (event, player, etc.) is not found (404)."""

    def __init__(self, message: str = "Resource not found on vlr.gg") -> None:
        super().__init__(message, 404)


class RateLimitError(HTTPError):
    """Raised when vlr.gg rate limits the client (429)."""

    def __init__(self, message: str = "Too many requests to vlr.gg") -> None:
        super().__init__(message, 429)


class ClientError(HTTPError):
    """Raised for 4xx HTTP errors other than 404 and 429."""


class ServerError(HTTPError):
    """Raised for 5xx HTTP errors."""


class ParsingError(VlrdevapiError):
    """Raised when vlrdevapi fails to parse the HTML response."""


class DataNotFoundError(ParsingError):
    """Raised when the requested data is semantically absent from the page (e.g., roster not found)."""


class ParseStructureError(ParsingError):
    """Raised when the page structure is unexpected and cannot be parsed."""


class ValidationError(VlrdevapiError, ValueError):
    """Raised when input validation fails (invalid IDs, parameters, etc.).

    Also inherits from ValueError for backward compatibility with
    code that catches ``ValueError`` on invalid inputs.
    """
