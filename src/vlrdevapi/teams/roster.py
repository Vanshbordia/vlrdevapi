"""Team roster retrieval."""

from __future__ import annotations

from bs4 import BeautifulSoup

from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import RosterMember

_config = get_config()


def roster(team_id: int, timeout: float | None = None) -> list[RosterMember]:
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
    url = f"{_config.vlr_base}/team/{team_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    
    # Find the "Current Roster" section (avoid lambda in 'string' for type checker)
    roster_label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        text = extract_text(h2)
        if "Current" in text and "Roster" in text:
            roster_label = h2
            break
    if roster_label is None:
        return []
    
    # Get the roster card that follows
    roster_card = roster_label.find_next("div", class_="wf-card")
    if not roster_card:
        return []
    
    members: list[RosterMember] = []
    
    # Process all roster items
    for item in roster_card.select(".team-roster-item"):
        anchor = item.select_one("a[href]")
        if not anchor:
            continue
        
        # Extract player ID from URL
        href_val = anchor.get("href")
        href = href_val if isinstance(href_val, str) else None
        player_id = extract_id_from_url(href, "player")
        
        # Extract photo URL
        photo_url = None
        photo_img = item.select_one(".team-roster-item-img img")
        if photo_img:
            src_val = photo_img.get("src")
            src = src_val if isinstance(src_val, str) else None
            # Skip placeholder images
            if src and "ph/sil.png" not in src:
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
                classes_val = flag.get("class")
                classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                for cls in classes:
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
