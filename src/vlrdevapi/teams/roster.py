"""Team roster retrieval."""

from __future__ import annotations

from typing import List
from bs4 import BeautifulSoup

from ..constants import VLR_BASE, DEFAULT_TIMEOUT
from ..countries import map_country_code
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import RosterMember


def roster(team_id: int, timeout: float = DEFAULT_TIMEOUT) -> List[RosterMember]:
    """
    Get current team roster (active players and staff).
    
    Args:
        team_id: Team ID
        timeout: Request timeout in seconds
    
    Returns:
        List of current roster members (players and staff)
    
    Example:
        >>> import vlrdevapi as vlr
        >>> roster = vlr.teams.roster(team_id=1034)
        >>> for member in roster:
        ...     print(f"{member.ign} ({member.role}) - {member.country}")
    """
    url = f"{VLR_BASE}/team/{team_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    
    # Find the "Current Roster" section
    roster_label = soup.find("h2", class_="wf-label mod-large", string=lambda t: t and "Current" in t and "Roster" in t)
    if not roster_label:
        return []
    
    # Get the roster card that follows
    roster_card = roster_label.find_next("div", class_="wf-card")
    if not roster_card:
        return []
    
    members: List[RosterMember] = []
    
    # Process all roster items
    for item in roster_card.select(".team-roster-item"):
        anchor = item.select_one("a[href]")
        if not anchor:
            continue
        
        # Extract player ID from URL
        href = anchor.get("href", "")
        player_id = extract_id_from_url(href, "player")
        
        # Extract photo URL
        photo_url = None
        photo_img = item.select_one(".team-roster-item-img img")
        if photo_img and photo_img.get("src"):
            src = photo_img.get("src")
            # Skip placeholder images
            if "ph/sil.png" not in src:
                photo_url = absolute_url(src)
        
        # Extract IGN (in-game name)
        alias_el = item.select_one(".team-roster-item-name-alias")
        ign = None
        is_captain = False
        country = None
        
        if alias_el:
            # Check for captain star
            captain_icon = alias_el.select_one("i.fa-star")
            if captain_icon:
                is_captain = True
            
            # Extract country from flag
            flag = alias_el.select_one(".flag")
            if flag:
                for cls in flag.get("class", []):
                    if cls.startswith("mod-") and cls != "mod-dark":
                        code = cls.removeprefix("mod-")
                        country = map_country_code(code)
                        break
            
            # Get IGN text (remove flag and star icons)
            ign_text = extract_text(alias_el)
            if ign_text:
                ign = ign_text.strip()
        
        # Extract real name
        real_name_el = item.select_one(".team-roster-item-name-real")
        real_name = extract_text(real_name_el) if real_name_el else None
        
        # Extract role
        role_el = item.select_one(".team-roster-item-name-role")
        role = "Player"  # Default role
        if role_el:
            role_text = extract_text(role_el).strip()
            if role_text:
                # Capitalize properly (e.g., "head coach" -> "Head Coach")
                role = role_text.title()
        
        members.append(RosterMember(
            player_id=player_id,
            ign=ign,
            real_name=real_name,
            country=country,
            role=role,
            is_captain=is_captain,
            photo_url=photo_url,
        ))
    
    return members
