"""
VLR Dev API - Python client for Valorant esports data from VLR.gg

Clean, intuitive API with better naming conventions and full type safety.

Example usage:
    >>> import vlrdevapi as vlr
    >>> 
    >>> # Get upcoming matches
    >>> matches = vlr.matches.upcoming(limit=10)
    >>> for match in matches:
    ...     print(f"{match.team1.name} vs {match.team2.name}")
    >>> 
    >>> # Get player profile
    >>> profile = vlr.players.profile(player_id=123)
    >>> print(f"{profile.handle} from {profile.country}")
    >>> 
    >>> # Get series info
    >>> info = vlr.series.info(match_id=456)
    >>> print(f"{info.teams[0].name} vs {info.teams[1].name}")
    >>> 
    >>> # Get team info and roster
    >>> team = vlr.teams.info(team_id=1034)
    >>> print(f"{team.name} ({team.tag}) - {team.country}")
    >>> roster = vlr.teams.roster(team_id=1034)
    >>> for member in roster:
    ...     print(f"{member.ign} - {member.role}")
"""

__version__ = "1.6.0"

# Configure stdout/stderr error handling without changing the environment's encoding.
# This avoids UnicodeEncodeError on legacy consoles while preventing decoding mismatches
# in subprocess readers (e.g., Sphinx doctest capturing with cp1252 on Windows).
import sys
import io

def _soft_configure_stream(stream: object) -> None:
    try:
        # Prefer Python 3.7+ API to keep existing encoding and only relax errors
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='replace')  # type: ignore[attr-defined]
            return
    except Exception:
        pass
    # Fallback: wrap using the same encoding if available
    try:
        encoding = getattr(stream, 'encoding', None) or 'utf-8'
        buffer = getattr(stream, 'buffer', None)
        if buffer is not None:
            wrapped = io.TextIOWrapper(buffer, encoding=encoding, errors='replace', line_buffering=True)
            # Assign back only if it looks like a real text stream
            if stream is sys.stdout:
                sys.stdout = wrapped  # type: ignore[assignment]
            elif stream is sys.stderr:
                sys.stderr = wrapped  # type: ignore[assignment]
    except Exception:
        # Best-effort: ignore if the environment is unusual (e.g., IDE-managed streams)
        pass

if sys.stdout is not None:
    _soft_configure_stream(sys.stdout)
if sys.stderr is not None:
    _soft_configure_stream(sys.stderr)

# Import modules for clean API access
from . import matches
from . import events
from . import players
from . import series
from . import status
from . import teams
from . import search

# Import enums and helper models for autocomplete
from .events import EventTier, EventStatus, EventStage

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

# Import rate limit configuration and helpers
from .fetcher import configure_rate_limit, get_rate_limit, reset_rate_limit

# Import configuration functions
from .config import configure, reset_config

__all__ = [
    # Modules - these are the main API entry points
    "matches",
    "events",
    "players",
    "series",
    "status",
    "teams",
    "search",
    
    # Enums for autocomplete
    "EventTier",
    "EventStatus",
    "EventStage",
    
    # Exceptions for error handling
    "VlrdevapiError",
    "NetworkError",
    "ScrapingError",
    "DataNotFoundError",
    "RateLimitError",
    
    # Convenience functions
    "check_status",
    "configure_rate_limit",
    "get_rate_limit",
    "reset_rate_limit",
    "configure",
    "reset_config",
]

# Note: Models are NOT exported at the top level to prevent confusion.
# Access them through their modules:
#   - vlr.matches.upcoming() returns Match objects
#   - vlr.players.profile() returns Profile objects
#   - vlr.events.info() returns Info objects
#   - etc.
