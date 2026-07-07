"""Input validation decorator for namespace methods."""

__all__ = ["sanitize_and_validate"]

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

from pydantic import validate_call

from vlrdevapi.exceptions import ValidationError

_ID_PARAMS = frozenset({"event_id", "team_id", "player_id", "series_id", "page", "limit", "subseries_id", "last_days"})
_MAX_PAGE_PARAMS = frozenset({"max_page"})


def _validate_bound_args(sig: inspect.Signature, args: tuple, kwargs: dict) -> inspect.BoundArguments:
    """Validate and sanitize bound arguments.

    Args:
        sig: The function signature to bind against.
        args: Positional arguments to validate.
        kwargs: Keyword arguments to validate.

    Returns:
        inspect.BoundArguments: The bound arguments after validation and
            sanitization.

    Raises:
        ValidationError: If any argument fails validation checks.

    """
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()

    for name, value in bound.arguments.items():
        # Positive-integer validation for known ID / pagination params
        # Skip None — these params are optional in some namespaces (e.g. event_id on team stats)
        if name in _ID_PARAMS and value is not None:
            if not isinstance(value, int) or value <= 0:
                msg = f"{name} must be a positive integer, got {value}"
                raise ValidationError(msg)

        # max_page allows 0 (meaning unlimited), but not negative
        if name in _MAX_PAGE_PARAMS and value is not None:
            if not isinstance(value, int) or value < 0:
                msg = f"{name} must be a non-negative integer, got {value}"
                raise ValidationError(msg)

        # game_id may be int or "all"
        if name == "game_id" and value != "all":
            if value is None:
                msg = "game_id cannot be None"
                raise ValidationError(msg)
            try:
                val = int(value)
            except (ValueError, TypeError):
                msg = f"game_id must be a positive integer or 'all', got {value}"
                raise ValidationError(
                    msg,
                ) from None
            if val <= 0:
                msg = f"game_id must be a positive integer or 'all', got {value}"
                raise ValidationError(
                    msg,
                )

        # Sanitize strings by stripping whitespace
        if isinstance(value, str):
            bound.arguments[name] = value.strip()

    return bound


def sanitize_and_validate(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function to validate its arguments via Pydantic type hints and positive-ID checks.

    Args:
        func: The function to wrap with validation.

    Returns:
        Callable[..., Any]: The wrapped function with input validation applied.

    """
    pydantic_validated = validate_call(validate_return=False)(func)
    sig = inspect.signature(func)

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = _validate_bound_args(sig, args, kwargs)
        return pydantic_validated(*bound.args, **bound.kwargs)

    sync_wrapper.__signature__ = sig  # type: ignore
    return sync_wrapper
