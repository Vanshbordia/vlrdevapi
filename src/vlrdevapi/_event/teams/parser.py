
from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.teams.models import Team


def parse_subnav(html: HTMLParser) -> list[tuple[str, str]]:
    """Parse subnav to get list of (stage_path, stage_name)."""
    subnav = html.css_first(".wf-subnav")
    if not subnav:
        return []

    stages = []
    for a in subnav.css("a.wf-subnav-item"):
        href = a.attributes.get("href", "")
        if href:
            title_el = a.css_first(".wf-subnav-item-title")
            stage_name = title_el.text(strip=True) if title_el else ""
            if not stage_name:
                # Fallback to last part of href
                stage_name = href.split("/")[-1].replace("-", " ").title()
            stages.append((href, stage_name))
    return stages


def parse_teams(html: HTMLParser) -> list[Team]:
    """Parse the Participating Teams section."""
    teams_section = html.css_first("h2.wf-label.mod-large")
    if not teams_section or "Participating Teams" not in teams_section.text():
        return []

    # Find the container, assuming it's after the h2
    # The teams are in .wf-card.event-team
    team_cards = html.css(".wf-card.event-team")
    teams = []
    seen_ids = set()

    for card in team_cards:
        team = _parse_team_card(card)
        if team and team.id not in seen_ids:
            teams.append(team)
            seen_ids.add(team.id)

    return teams


def _parse_team_card(card: Node) -> Team | None:
    """Parse a single team card."""
    name_el = card.css_first(".event-team-name")
    if not name_el:
        return None

    name = name_el.text(strip=True)

    a_el = name_el.css_first("a")
    if not a_el:
        return None

    href = a_el.attributes.get("href", "")
    # /team/1034/nrg
    if href and "/team/" in href:
        try:
            id_str = href.split("/team/")[1].split("/")[0]
            team_id = int(id_str)
        except (ValueError, IndexError):
            return None
    else:
        return None

    note_el = card.css_first(".event-team-note")
    note = note_el.text(strip=True) if note_el else None

    return Team(name=name, id=team_id, note=note)
