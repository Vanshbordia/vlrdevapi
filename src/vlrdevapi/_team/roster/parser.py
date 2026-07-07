
from selectolax.parser import HTMLParser, Node

from vlrdevapi._team.roster.models import Player, TeamRoster
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.exceptions import DataNotFoundError, ParseStructureError


def parse_team_roster(html: HTMLParser) -> TeamRoster:
    """Parse team roster from team page HTML.

    Args:
        html: Parsed HTML of the team page.

    Returns:
        TeamRoster: Parsed roster with ``players`` and ``staff`` lists.

    Raises:
        DataNotFoundError: If no roster section is found on the page.
        ParseStructureError: If the roster container structure is unexpected.

    """
    roster = TeamRoster()

    # Find the roster section
    roster_h2s = html.css("h2.wf-label.mod-large")
    roster_h2 = None
    for h2 in roster_h2s:
        h2_text = h2.text(strip=True).replace("\t", " ").replace("  ", " ")
        if "Current Roster" in h2_text:
            roster_h2 = h2
            break
    if not roster_h2:
        msg = "roster not found on team page"
        raise DataNotFoundError(msg)

    # Find the wf-card div after the h2
    roster_card = roster_h2.next
    while roster_card and not (
        roster_card.tag == "div"
        and "wf-card" in (roster_card.attributes.get("class") or "")
    ):
        roster_card = roster_card.next
    if not roster_card:
        msg = "roster container not found on team page"
        raise ParseStructureError(msg)

    # Find sections for players and staff
    sections = roster_card.css(".wf-module-label")
    for section in sections:
        section_type = section.text(strip=True).lower()
        container = section.next
        while container and container.tag in ("-text", "-comment"):
            container = container.next
        if not container or container.tag != "div":
            continue

        items = container.css(".team-roster-item")
        players = []
        for item in items:
            player = _parse_roster_item(item, section_type)
            if player:
                players.append(player)

        if section_type == "players":
            roster.players = players
        elif section_type == "staff":
            roster.staff = players

    return roster


def _parse_roster_item(item: Node, section_type: str) -> Player | None:
    """Parse individual roster item.

    Args:
        item: The roster item HTML node.
        section_type: The section type (``"players"`` or ``"staff"``).

    Returns:
        Player | None: The parsed player/staff member, or ``None``
        if parsing failed.

    """
    player = Player(id=0)

    # Extract ID from href
    a_el = item.css_first("a")
    if a_el:
        href = a_el.attributes.get("href") or ""
        if "/player/" in href:
            parts = href.split("/player/")[-1].split("/")
            if parts and parts[0].isdigit():
                player.id = int(parts[0])

    # Extract photo URL
    img_el = item.css_first("img")
    if img_el:
        src = img_el.attributes.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        player.photo_url = src

    # Extract IGN and captain
    alias_el = item.css_first(".team-roster-item-name-alias")
    if alias_el:
        text = alias_el.text(strip=True)
        # Remove flag and star
        star_el = alias_el.css_first(".fa.fa-star")
        if star_el:
            player.is_captain = True
            # Remove star text
            star_text = star_el.text(strip=True)
            text = text.replace(star_text, "").strip()
        # Country flag
        flag_el = alias_el.css_first(".flag")
        if flag_el:
            class_attr = flag_el.attributes.get("class") or ""
            if "flag mod-" in class_attr:
                code = class_attr.split("mod-")[-1].split()[0]
                player.country = get_country_name(code)
            flag_text = flag_el.text(strip=True)
            text = text.replace(flag_text, "").strip()
        player.ign = text

    # Extract real name
    real_name_el = item.css_first(".team-roster-item-name-real")
    if real_name_el:
        player.real_name = real_name_el.text(strip=True)

    # Extract roles
    role_els = item.css(".wf-tag.mod-light.team-roster-item-name-role")
    roles = []
    for role_el in role_els:
        role_text = role_el.text(strip=True).title()  # Capitalize
        roles.append(role_text)
        if role_text == "Inactive":
            player.is_active = False
        elif role_text == "Sub":
            player.is_sub = True

    if not roles:
        roles = ["Player"] if section_type == "players" else ["Staff"]
    player.roles = roles

    return player
