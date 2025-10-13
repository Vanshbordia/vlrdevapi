"""
VLR Dev API - Python client for Valorant esports data from VLR.gg

Clean, intuitive API with better naming conventions and full type safety.

Example usage:
    >>> import vlrdevapi as vlr
    >>> 
    >>> # Get upcoming matches
    >>> matches = vlr.matches.upcoming(limit=10)
    >>> for match in matches:
    ...     print(f"{match.teams[0]} vs {match.teams[1]}")
    >>> 
    >>> # Get player profile
    >>> profile = vlr.players.profile(player_id=123)
    >>> print(f"{profile.handle} from {profile.country}")
    >>> 
    >>> # Get series info
    >>> info = vlr.series.info(match_id=456)
    >>> print(f"{info.teams[0].name} vs {info.teams[1].name}")
"""

__version__ = "1.0.0"

# Import modules for clean API access
from . import matches
from . import events
from . import players
from . import series
from . import status

# Import exceptions for error handling
from .exceptions import (
    VlrdevapiError,
    NetworkError,
    ScrapingError,
    DataNotFoundError,
    RateLimitError,
)

# Import status function for convenience
from .status import check_status

__all__ = [
    # Modules - these are the main API entry points
    "matches",
    "events",
    "players",
    "series",
    "status",
    
    # Exceptions for error handling
    "VlrdevapiError",
    "NetworkError",
    "ScrapingError",
    "DataNotFoundError",
    "RateLimitError",
    
    # Convenience function
    "check_status",
]

# Note: Models are NOT exported at the top level to prevent confusion.
# Access them through their modules:
#   - vlr.matches.upcoming() returns Match objects
#   - vlr.players.profile() returns Profile objects
#   - vlr.events.info() returns Info objects
#   - etc.
