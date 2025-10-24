"""Configuration system for vlrdevapi."""

from __future__ import annotations

from typing import Optional


class Config:
    """Global configuration for vlrdevapi.

    This class holds all configurable settings for the library.
    Settings can be modified globally to customize behavior.
    """

    def __init__(self) -> None:
        # Base URL
        self.vlr_base = "https://www.vlr.gg"

        # HTTP settings
        self.default_timeout = 5.0
        self.default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.max_retries = 3
        self.backoff_factor = 1.0

        # Rate limiting settings
        self.default_rate_limit = 10  # requests per second
        self.default_rate_limit_enabled = True

    def update(
        self,
        vlr_base: Optional[str] = None,
        default_timeout: Optional[float] = None,
        default_user_agent: Optional[str] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        default_rate_limit: Optional[float] = None,
        default_rate_limit_enabled: Optional[bool] = None,
    ) -> None:
        """Update configuration settings.

        Args:
            vlr_base: Base URL for VLR.gg
            default_timeout: Default request timeout in seconds
            default_user_agent: Default User-Agent header
            max_retries: Maximum number of retries for failed requests
            backoff_factor: Backoff multiplier for retry delays
            default_rate_limit: Default requests per second limit
            default_rate_limit_enabled: Whether rate limiting is enabled by default
        """
        if vlr_base is not None:
            self.vlr_base = vlr_base
        if default_timeout is not None:
            self.default_timeout = default_timeout
        if default_user_agent is not None:
            self.default_user_agent = default_user_agent
        if max_retries is not None:
            self.max_retries = max_retries
        if backoff_factor is not None:
            self.backoff_factor = backoff_factor
        if default_rate_limit is not None:
            self.default_rate_limit = default_rate_limit
        if default_rate_limit_enabled is not None:
            self.default_rate_limit_enabled = default_rate_limit_enabled

    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values."""
        self.__init__()


# Global configuration instance
_global_config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return _global_config


def configure(
    vlr_base: Optional[str] = None,
    default_timeout: Optional[float] = None,
    default_user_agent: Optional[str] = None,
    max_retries: Optional[int] = None,
    backoff_factor: Optional[float] = None,
    default_rate_limit: Optional[float] = None,
    default_rate_limit_enabled: Optional[bool] = None,
) -> None:
    """Configure global settings for vlrdevapi.

    This function allows you to customize various aspects of the library's behavior.

    Args:
        vlr_base: Base URL for VLR.gg (default: "https://www.vlr.gg")
        default_timeout: Default request timeout in seconds (default: 5.0)
        default_user_agent: Default User-Agent header (default: Chrome-like string)
        max_retries: Maximum number of retries for failed requests (default: 3)
        backoff_factor: Backoff multiplier for retry delays (default: 1.0)
        default_rate_limit: Default requests per second limit (default: 10)
        default_rate_limit_enabled: Whether rate limiting is enabled by default (default: True)

    Example:
        >>> import vlrdevapi as vlr
        >>>
        >>> # Increase timeout for slow connections
        >>> vlr.configure(default_timeout=10.0)
        >>>
        >>> # Disable rate limiting for high-throughput applications
        >>> vlr.configure(default_rate_limit_enabled=False)
        >>>
        >>> # Use custom User-Agent
        >>> vlr.configure(default_user_agent="MyApp/1.0")
        >>>
        >>> # Increase retry attempts
        >>> vlr.configure(max_retries=5, backoff_factor=2.0)
    """
    _global_config.update(
        vlr_base=vlr_base,
        default_timeout=default_timeout,
        default_user_agent=default_user_agent,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        default_rate_limit=default_rate_limit,
        default_rate_limit_enabled=default_rate_limit_enabled,
    )


def reset_config() -> None:
    """Reset all configuration settings to their default values.

    Example:
        >>> import vlrdevapi as vlr
        >>> vlr.reset_config()  # Reset to defaults
    """
    _global_config.reset_to_defaults()
