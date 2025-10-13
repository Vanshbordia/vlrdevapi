"""VLR.gg status checking utilities."""

from urllib import request

from .constants import VLR_BASE, DEFAULT_TIMEOUT
from .exceptions import NetworkError


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
        with request.urlopen(req, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 500) < 400
    except Exception:
        return False
