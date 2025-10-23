"""VLR.gg status checking utilities."""

from urllib import request
from http.client import HTTPResponse
from typing import cast

from .constants import VLR_BASE, DEFAULT_TIMEOUT


def check_status(timeout: float = DEFAULT_TIMEOUT) -> bool:
    """
    Check if vlr.gg is accessible.
    
    Args:
        timeout: Request timeout in seconds.
    
    Returns:
        True if vlr.gg responds with a successful status code.
    """
    url = f"{VLR_BASE}/"
    req = request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        # Cast to a concrete response type to avoid Any in type checking
        with cast(HTTPResponse, request.urlopen(req, timeout=timeout)) as response:
            status: int = getattr(response, "status", 500)
            return 200 <= status < 400
    except Exception:
        return False
