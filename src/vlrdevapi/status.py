"""VLR.gg status checking utilities."""

from urllib import request
from http.client import HTTPResponse
from typing import cast

from .config import get_config


_config = get_config()


def check_status(timeout: float = None) -> bool:
    """
    Check if vlr.gg is accessible.
    
    Args:
        timeout: Request timeout in seconds.
    
    Returns:
        True if vlr.gg responds with a successful status code.
    """
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    url = f"{_config.vlr_base}/"
    req = request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        # Cast to a concrete response type to avoid Any in type checking
        with cast(HTTPResponse, request.urlopen(req, timeout=effective_timeout)) as response:
            status: int = getattr(response, "status", 500)
            return 200 <= status < 400
    except Exception:
        return False
