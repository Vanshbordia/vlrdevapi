"""Event teams functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .models import Team
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, extract_id_from_url

_config = get_config()


def teams(event_id: int, timeout: float | None = None) -> list[Team]:
    """
    Get teams participating in an event.

    Args:
        event_id: Event ID
        timeout: Request timeout in seconds

    Returns:
        List of teams in the event

    Example:
        >>> import vlrdevapi as vlr
        >>> teams = vlr.events.teams(event_id=123)
        >>> for team in teams:
        ...     print(f"{team.name} (ID: {team.id}) - Type: {team.type}")
    """
    url = f"{_config.vlr_base}/event/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []

    soup = BeautifulSoup(html, "lxml")

    teams_list: list[Team] = []

    # Find the event teams container
    teams_container = soup.select_one(".event-teams-container")
    if not teams_container:
        return []

    # Find all team cards within the container
    team_cards = teams_container.select(".event-team")

    seen_teams: set[int] = set()

    for team_card in team_cards:
        # Get the team name link
        team_name_element = team_card.select_one(".event-team-name")
        if not team_name_element:
            continue

        href = team_name_element.get("href")
        if not href or "/team/" not in href:
            continue

        team_id = extract_id_from_url(href, "team")
        if not team_id:
            continue

        if team_id in seen_teams:
            continue

        # Extract team name
        team_name = extract_text(team_name_element) or "Unknown Team"

        # Extract team type from the note element
        team_note_element = team_card.select_one(".event-team-note")
        team_type = None
        if team_note_element:
            # Check if the note contains a link (like Ascension 2023 link)
            link_in_note = team_note_element.select_one("a")
            if link_in_note:
                team_type = extract_text(link_in_note) or extract_text(team_note_element)
            else:
                team_type = extract_text(team_note_element)

            # Clean up the type text (remove extra spaces, etc.)
            if team_type:
                team_type = team_type.strip()

        teams_list.append(Team(
            id=team_id,
            name=team_name.strip(),
            type=team_type
        ))

        seen_teams.add(team_id)

    return teams_list