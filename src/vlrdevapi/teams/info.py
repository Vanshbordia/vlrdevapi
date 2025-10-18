"""Team information retrieval."""

from __future__ import annotations

from typing import List, Optional
from bs4 import BeautifulSoup

from ..constants import VLR_BASE, DEFAULT_TIMEOUT
from ..countries import map_country_code
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import TeamInfo, SocialLink, PreviousTeam, SuccessorTeam


def info(team_id: int, timeout: float = DEFAULT_TIMEOUT) -> Optional[TeamInfo]:
    """
    Get team information.
    
    Args:
        team_id: Team ID
        timeout: Request timeout in seconds
    
    Returns:
        Team information or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> team = vlr.teams.info(team_id=1034)
        >>> print(f"{team.name} ({team.tag}) - {team.country}")
    """
    url = f"{VLR_BASE}/team/{team_id}"
    try:
        html = fetch_html(url, timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".team-header")
    
    if not header:
        return None
    
    # Extract team name
    name_el = header.select_one("h1.wf-title")
    name = extract_text(name_el) if name_el else None
    
    # Extract team tag
    tag_el = header.select_one("h2.team-header-tag")
    tag = extract_text(tag_el) if tag_el else None
    
    # Extract logo URL
    logo_url = None
    logo_img = header.select_one(".team-header-logo img")
    if logo_img and logo_img.get("src"):
        logo_url = absolute_url(logo_img.get("src"))
    
    # Check if team is active
    is_active = True
    status_el = header.select_one(".team-header-status")
    if status_el:
        status_text = extract_text(status_el).lower()
        if "inactive" in status_text:
            is_active = False
    
    # Extract country
    country = None
    country_el = header.select_one(".team-header-country")
    if country_el:
        flag = country_el.select_one(".flag")
        if flag:
            for cls in flag.get("class", []):
                if cls.startswith("mod-") and cls != "mod-dark":
                    code = cls.removeprefix("mod-")
                    country = map_country_code(code)
                    break
    
    # Extract social links
    socials: List[SocialLink] = []
    links_container = header.select_one(".team-header-links")
    if links_container:
        for anchor in links_container.select("a[href]"):
            href = anchor.get("href", "").strip()
            label = extract_text(anchor).strip()
            # Skip empty links
            if href and label and href != "":
                full_url = absolute_url(href) or href
                socials.append(SocialLink(label=label, url=full_url))
    
    # Extract previous and current team information
    previous_team = None
    current_team = None
    successor_el = header.select_one(".team-header-name-successor")
    if successor_el:
        successor_text = extract_text(successor_el).lower()
        link = successor_el.select_one("a[href]")
        if link:
            href = link.get("href", "")
            linked_team_id = extract_id_from_url(href, "team")
            linked_name = extract_text(link)
            if linked_name:
                if "previously" in successor_text:
                    previous_team = PreviousTeam(team_id=linked_team_id, name=linked_name)
                if "currently" in successor_text:
                    current_team = SuccessorTeam(team_id=linked_team_id, name=linked_name)
    
    return TeamInfo(
        team_id=team_id,
        name=name,
        tag=tag,
        logo_url=logo_url,
        country=country,
        is_active=is_active,
        socials=socials,
        previous_team=previous_team,
        current_team=current_team,
    )
