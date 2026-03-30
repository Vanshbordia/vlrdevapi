"""Team information retrieval."""

from __future__ import annotations

from bs4 import BeautifulSoup

from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

from .models import TeamInfo, SocialLink, PreviousTeam, SuccessorTeam

_config = get_config()


def info(team_id: int, timeout: float | None = None) -> TeamInfo | None:
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
    url = f"{_config.vlr_base}/team/{team_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    
    # Fetch page with light mode (dm=0)
    try:
        html_light = fetch_html(url, effective_timeout, cookies={"dm": "0"})
    except NetworkError:
        return None

    # Fetch page with dark mode (dm=1)
    try:
        html_dark = fetch_html(url, effective_timeout, cookies={"dm": "1"})
    except NetworkError:
        html_dark = html_light  # Fallback to light mode if dark mode fails

    soup_light = BeautifulSoup(html_light, "lxml")
    soup_dark = BeautifulSoup(html_dark, "lxml")
    
    header_light = soup_light.select_one(".team-header")
    header_dark = soup_dark.select_one(".team-header")

    if not header_light:
        return None

    # Extract team name
    name_el = header_light.select_one("h1.wf-title")
    name = extract_text(name_el) if name_el else None

    # Extract team tag
    tag_el = header_light.select_one("h2.team-header-tag")
    tag = extract_text(tag_el) if tag_el else None

    # Extract logo URL for light mode
    logo_url_light: str | None = None
    logo_img_light = header_light.select_one(".team-header-logo img")
    if logo_img_light:
        src_val = logo_img_light.get("src")
        src = src_val if isinstance(src_val, str) else None
        if src:
            logo_url_light = absolute_url(src)

    # Extract logo URL for dark mode
    logo_url_dark: str | None = None
    logo_img_dark = header_dark.select_one(".team-header-logo img")
    if logo_img_dark:
        src_val = logo_img_dark.get("src")
        src = src_val if isinstance(src_val, str) else None
        if src:
            logo_url_dark = absolute_url(src)

    # Use light mode logo as the default logo_url for backward compatibility
    logo_url = logo_url_light

    # Check if team is active
    is_active = True
    status_el = header_light.select_one(".team-header-status")
    if status_el:
        status_text = extract_text(status_el).lower()
        if "inactive" in status_text:
            is_active = False

    # Extract country
    country: str | None = None
    country_el = header_light.select_one(".team-header-country")
    if country_el:
        flag = country_el.select_one(".flag")
        if flag:
            classes_val = flag.get("class")
            classes: list[str] = [c for c in classes_val if isinstance(c, str)] if isinstance(classes_val, (list, tuple)) else []
            for cls in classes:
                if cls.startswith("mod-") and cls != "mod-dark":
                    code = cls.removeprefix("mod-")
                    country = map_country_code(code)
                    break

    # Extract social links
    socials: list[SocialLink] = []
    links_container = header_light.select_one(".team-header-links")
    if links_container:
        for anchor in links_container.select("a[href]"):
            href_val = anchor.get("href")
            href = (href_val if isinstance(href_val, str) else "").strip()
            label = extract_text(anchor).strip()
            # Skip empty links
            if href and label and href != "":
                full_url = absolute_url(href) or href
                socials.append(SocialLink(label=label, url=full_url))

    # Extract previous and current team information
    previous_team: PreviousTeam | None = None
    current_team: SuccessorTeam | None = None
    successor_el = header_light.select_one(".team-header-name-successor")
    if successor_el:
        successor_text = extract_text(successor_el).lower()
        link = successor_el.select_one("a[href]")
        if link:
            href_val = link.get("href")
            href = href_val if isinstance(href_val, str) else None
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
        logo_url_light=logo_url_light,
        logo_url_dark=logo_url_dark,
        country=country,
        is_active=is_active,
        socials=socials,
        previous_team=previous_team,
        current_team=current_team,
    )
