"""Common utilities, types, and decorators for vlrdevapi MCP server."""

from __future__ import annotations

import functools
import json
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    # Backward compatibility with older mcp versions
    from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore[no-redef]

from vlrdevapi.commons.export import ExportableModel
from vlrdevapi.exceptions import (
    NotFoundError,
    ParsingError,
    RateLimitError,
    RequestError,
    ValidationError,
)

F = TypeVar("F", bound=Callable[..., Any])


def serialize(result: Any, orient: str = "model") -> str:
    """Serialize vlrdevapi models, dicts, lists, or primitive objects to JSON."""
    if isinstance(result, ExportableModel):
        return result.to_json(indent=2, orient=orient) or ""
    if isinstance(result, BaseModel):
        return result.model_dump_json(indent=2)
    if isinstance(result, (dict, list)):
        return json.dumps(result, indent=2, default=str)
    return str(result)


def handle_errors(func: F) -> F:
    """Decorator to trap common vlrdevapi exceptions and return structured JSON."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            res = func(*args, **kwargs)
            return serialize(res)
        except NotFoundError as e:
            return json.dumps({"error": "NotFound", "message": str(e)}, indent=2)
        except RateLimitError as e:
            return json.dumps({"error": "RateLimited", "message": str(e)}, indent=2)
        except ValidationError as e:
            return json.dumps({"error": "ValidationError", "message": str(e)}, indent=2)
        except (RequestError, ParsingError) as e:
            return json.dumps({"error": type(e).__name__, "message": str(e)}, indent=2)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"error": "UnexpectedError", "message": str(e)}, indent=2)

    return wrapper  # type: ignore[return-value]


__all__ = ["MCPServer", "handle_errors", "serialize"]
