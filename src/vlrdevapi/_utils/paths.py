"""Centralized URL path constants for vlr.gg API."""


MATCHES = "/matches"
MATCHES_RESULTS = "/matches/results"


def series(series_id: int) -> str:
    """Build a URL path for a series page.

    Args:
        series_id: The series ID.

    Returns:
        str: The URL path ``"/<series_id>"``.

    """
    return f"/{series_id}"


def event(event_id: int) -> str:
    """Build a URL path for an event page.

    Args:
        event_id: The event ID.

    Returns:
        str: The URL path ``"/event/<event_id>"``.

    """
    return f"/event/{event_id}"


def event_matches(event_id: int) -> str:
    """Build a URL path for an event's matches page.

    Args:
        event_id: The event ID.

    Returns:
        str: The URL path ``"/event/matches/<event_id>"``.

    """
    return f"/event/matches/{event_id}"


def team(team_id: int) -> str:
    """Build a URL path for a team page.

    Args:
        team_id: The team ID.

    Returns:
        str: The URL path ``"/team/<team_id>"``.

    """
    return f"/team/{team_id}"


def team_matches(team_id: int) -> str:
    """Build a URL path for a team's matches page.

    Args:
        team_id: The team ID.

    Returns:
        str: The URL path ``"/team/matches/<team_id>"``.

    """
    return f"/team/matches/{team_id}"


def player(player_id: int) -> str:
    """Build a URL path for a player page.

    Args:
        player_id: The player ID.

    Returns:
        str: The URL path ``"/player/<player_id>"``.

    """
    return f"/player/{player_id}"
