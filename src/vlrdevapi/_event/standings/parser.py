"""Event standings parser."""

from selectolax.parser import HTMLParser, Node

from vlrdevapi._event.standings.models import StandingEntry, TeamStanding
from vlrdevapi.commons.prizes import parse_prize_amount
import contextlib


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


def parse_standings(html: HTMLParser) -> list[StandingEntry]:
    """Parse the Prize Distribution section."""
    # Find the Prize Distribution label (can be h2 or div)
    labels = html.css(".wf-label.mod-large")
    target_label = None
    for label in labels:
        if "Prize Distribution" in label.text():
            target_label = label
            break

    if not target_label:
        return []

    # Find the wf-card mod-dark containing the table
    # It's usually a sibling or inside a sibling card
    table = html.css_first(".wf-ptable--standings")
    if not table:
        return []

    standings = []
    rows = table.css("div.row")
    if len(rows) < 2:
        return []

    # Parse header to get column indices
    header_cells = [c.text(strip=True).lower() for c in rows[0].css("div.cell")]
    points_idx = None
    note_idx = None
    for i, h in enumerate(header_cells):
        if "points" in h:
            points_idx = i
        elif "note" in h:
            note_idx = i

    # Skip header row
    for row in rows[1:]:
        entry = _parse_standing_row(row, points_idx, note_idx)
        if entry:
            standings.append(entry)

    return standings


def _parse_standing_row(
    row: Node, points_idx: int | None, note_idx: int | None,
) -> StandingEntry | None:
    """Parse a single standing row."""
    cells = row.css("div.cell")
    if len(cells) < 3:  # At least place, prize, team
        return None

    # Place
    place = cells[0].text(strip=True)

    # Prize
    prize_text = cells[1].text(strip=True)
    prize_money, prize_currency = parse_prize_amount(prize_text)

    # Team
    team_cell = cells[2]
    team = _parse_team_from_cell(team_cell)
    if not team:
        return None

    # Points (optional)  # noqa: ERA001
    points = None
    if points_idx is not None and len(cells) > points_idx:
        points_text = cells[points_idx].text(strip=True)
        if points_text:
            if points_text.startswith("+"):
                with contextlib.suppress(ValueError):
                    points = int(points_text[1:])
            else:
                with contextlib.suppress(ValueError):
                    points = int(points_text)

    # Note (optional)  # noqa: ERA001
    note = None
    if note_idx is not None and len(cells) > note_idx:
        note_cell = cells[note_idx]
        note_el = note_cell.css_first("a")
        if note_el:
            note = note_el.text(strip=True)
        else:
            note_text = note_cell.text(strip=True)
            if note_text:
                note = note_text

    return StandingEntry(
        place=place,
        prize_money=prize_money,
        prize_currency=prize_currency,
        team=team,
        points=points,
        note=note,
    )



def _parse_team_from_cell(cell: Node) -> TeamStanding | None:
    """Parse team from team cell."""
    # Check for TBD
    ge_text_light = cell.css_first(".ge-text-light")
    if ge_text_light and "TBD" in ge_text_light.text():
        return TeamStanding(id=None, name="TBD", country=None, logo_url=None)

    # Normal team
    a_el = cell.css_first("a")
    if not a_el:
        return None

    href = a_el.attributes.get("href")
    team_id = None
    if href and "/team/" in href:
        try:
            id_str = href.split("/team/")[1].split("/")[0]
            team_id = int(id_str)
        except (ValueError, IndexError):
            pass

    # Name
    text_of = a_el.css_first(".text-of")
    name = text_of.text(deep=False, strip=True) if text_of else ""

    # Country
    country_el = a_el.css_first(".ge-text-light")
    country = country_el.text(strip=True) if country_el else None

    # Logo
    img_el = a_el.css_first("img")
    logo_url = img_el.attributes.get("src") if img_el else None
    if logo_url and logo_url.startswith("//"):
        logo_url = "https:" + logo_url

    return TeamStanding(id=team_id, name=name, country=country, logo_url=logo_url)
