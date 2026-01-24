"""Player profile functionality."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .models import Profile, SocialLink, Team
from ._parser import _parse_month_year
from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, absolute_url, extract_id_from_url

_config = get_config()


def profile(player_id: int, timeout: float | None = None) -> Profile | None:
    """
    Get player profile information.
    
    Args:
        player_id: Player ID
        timeout: Request timeout in seconds
    
    Returns:
        Player profile or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> profile = vlr.players.profile(player_id=123)
        >>> print(f"{profile.handle} from {profile.country}")
    """
    url = f"{_config.vlr_base}/player/{player_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".player-header")
    
    handle = extract_text(header.select_one("h1.wf-title")) if header else None
    real_name = extract_text(header.select_one(".player-real-name")) if header else None
    
    avatar_url = None
    if header:
        avatar_img = header.select_one(".wf-avatar img")
        if avatar_img:
            src_val = avatar_img.get("src")
            src = src_val if isinstance(src_val, str) else None
            if src:
                avatar_url = absolute_url(src)
    
    # Parse socials
    socials: list[SocialLink] = []
    if header:
        for anchor in header.select("a[href]"):
            href_val = anchor.get("href")
            href = href_val if isinstance(href_val, str) else None
            label = extract_text(anchor)
            if href and label:
                url_or = absolute_url(href) or href
                socials.append(SocialLink(label=label, url=url_or))
    
    # Parse country
    country = None
    if header:
        flag = header.select_one(".flag")
        if flag:
            classes_val = flag.get("class")
            classes: list[str] = list(classes_val) if isinstance(classes_val, (list, tuple)) else []
            for cls in classes:
                if cls.startswith("mod-") and cls != "mod-dark":
                    code: str = cls.removeprefix("mod-")
                    country = map_country_code(code)
                    break
    
    # Parse current teams
    current_teams: list[Team] = []
    label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        text = extract_text(h2) or ""
        if "current teams" in text.lower():
            label = h2
            break
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href_val = anchor.get("href")
                href = href_val.strip("/") if isinstance(href_val, str) else ""
                team_id = extract_id_from_url(href, "team") if href else None
                name_el = anchor.select_one("div[style][style*='font-weight']") or anchor
                team_name = extract_text(name_el).strip() if name_el else None
                
                role_el = anchor.select_one("span.wf-tag")
                role = extract_text(role_el).strip().title() if role_el else "Player"
                
                joined_date = None
                for meta in anchor.select(".ge-text-light"):
                    text = extract_text(meta)
                    if "joined" in text.lower():
                        joined_date = _parse_month_year(text)
                        break
                
                current_teams.append(Team(
                    id=team_id,
                    name=team_name,
                    role=role,
                    joined_date=joined_date,
                    left_date=None,
                ))
    
    # Parse aliases
    aliases: list[str] | None = None
    if header:
        # Look for spans that contain the text "aliases:"
        for span in header.find_all('span'):
            span_text = extract_text(span)
            if span_text and 'aliases:' in span_text.lower():
                if ":" in span_text:
                    aliases_part = span_text.split(":")[1].strip()
                    # Split by commas and clean up each alias
                    aliases = [alias.strip().strip('"\'') for alias in aliases_part.split(",")]
                    # Remove empty strings if any
                    aliases = [alias for alias in aliases if alias]
                    break

    # Parse past teams
    past_teams: list[Team] = []
    label = None
    for h2 in soup.select("h2.wf-label.mod-large"):
        text = extract_text(h2) or ""
        if "past teams" in text.lower():
            label = h2
            break
    if label:
        card = label.find_next("div", class_="wf-card")
        if card:
            for anchor in card.select("a.wf-module-item"):
                href_val = anchor.get("href")
                href = href_val.strip("/") if isinstance(href_val, str) else ""
                team_id = extract_id_from_url(href, "team") if href else None
                name_el = anchor.select_one("div[style][style*='font-weight']") or anchor
                team_name = extract_text(name_el).strip() if name_el else None

                role_el = anchor.select_one("span.wf-tag")
                role = extract_text(role_el).strip().title() if role_el else "Player"

                joined_date = None
                left_date = None
                for meta in anchor.select(".ge-text-light"):
                    text = extract_text(meta)
                    if "-" in text or "–" in text:
                        normalized = text.replace("\u2013", "-").replace("–", "-")
                        parts = [part.strip() for part in normalized.split("-") if part.strip()]
                        if parts:
                            joined_date = _parse_month_year(parts[0])
                            if len(parts) > 1 and "present" not in parts[1].lower():
                                left_date = _parse_month_year(parts[1])
                        break

                past_teams.append(Team(
                    id=team_id,
                    name=team_name,
                    role=role,
                    joined_date=joined_date,
                    left_date=left_date,
                ))
    
    return Profile(
        player_id=player_id,
        handle=handle,
        real_name=real_name,
        country=country,
        avatar_url=avatar_url,
        aliases=aliases,
        socials=socials,
        current_teams=current_teams,
        past_teams=past_teams,
    )
