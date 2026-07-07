
from urllib.parse import urlparse

from selectolax.parser import HTMLParser

from vlrdevapi._team.info.models import TeamInfo, TeamSocial, TeamSuccessor
from vlrdevapi.commons.countries import get_country_name


def parse_team_info(light_html: HTMLParser, dark_html: HTMLParser) -> TeamInfo:
    """Parse team information from team pages (light and dark mode).

    Args:
        light_html: Parsed HTML of the team page in light mode.
        dark_html: Parsed HTML of the team page in dark mode.

    Returns:
        TeamInfo: Parsed team information including name, tag, country,
        logo URLs, social links, and successor teams.

    """
    team = TeamInfo()

    # Use light_html for most parsing
    html = light_html

    # Try to get team name from title
    title_el = html.css_first("title")
    if title_el:
        title_text = title_el.text(strip=True)
        # Title format: "Team Name - VLR.gg"
        if " - VLR.gg" in title_text:
            team.name = title_text.replace(" - VLR.gg", "").strip()

    # Try to get team info from header
    header_el = html.css_first(".team-header")
    if header_el:
        # Get team name from h1.wf-title
        name_el = header_el.css_first("h1.wf-title")
        if name_el:
            team.name = name_el.text(strip=True)

        # Get team tag from h2.team-header-tag
        tag_el = header_el.css_first("h2.team-header-tag")
        if tag_el:
            team.tag = tag_el.text(strip=True)

        # If no tag found, try to extract from name if it's short
        if not team.tag and team.name and len(team.name) <= 4:
            team.tag = team.name

        # Get country
        country_el = header_el.css_first(".team-header-country .flag")
        if country_el:
            class_attr = country_el.attributes.get("class") or ""
            if "flag mod-" in class_attr:
                code = class_attr.split("mod-")[-1].split()[0]
                team.country = get_country_name(code)

        # Get is_active
        status_el = header_el.css_first(".team-header-status")
        if status_el and "(inactive)" in status_el.text(strip=True).lower():
            team.is_active = False

        # Get socials
        links_el = header_el.css_first(".team-header-links")
        if links_el:
            team.socials = []
            for a_el in links_el.css("a"):
                href = (a_el.attributes.get("href") or "").strip()
                text = a_el.text(strip=True)
                if href:
                    platform = map_social_platform(href, text)
                    if platform:
                        team.socials.append(TeamSocial(name=platform, url=href))

        # Get successors
        successor_el = header_el.css_first(".team-header-name-successor")
        if successor_el:
            text = successor_el.text(strip=True).lower()
            for a_el in successor_el.css("a"):
                href = (a_el.attributes.get("href") or "").strip()
                name = a_el.text(strip=True)
                if "/team/" in href:
                    try:
                        team_id = int(href.split("/team/")[-1].split("/")[0])
                        successor = TeamSuccessor(id=team_id, name=name)
                        if "previously" in text:
                            if team.previous_teams is None:
                                team.previous_teams = []
                            team.previous_teams.append(successor)
                        elif "currently" in text:
                            if team.current_teams is None:
                                team.current_teams = []
                            team.current_teams.append(successor)
                    except ValueError:
                        pass

    # Get logos from light and dark html
    team.light_logo_url = extract_logo_url(light_html)
    team.dark_logo_url = extract_logo_url(dark_html)

    return team


def extract_logo_url(html: HTMLParser) -> str:
    """Extract logo URL from HTML.

    Args:
        html: Parsed HTML containing the team header.

    Returns:
        str: The logo image URL, or empty string if not found.

    """
    logo_el = html.css_first(".team-header-logo img")
    if logo_el:
        src = logo_el.attributes.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        return src
    return ""


_PLATFORM_DOMAINS: dict[str, str] = {
    "twitch.tv": "Twitch",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "x.com": "X",
    "twitter.com": "X",
    "instagram.com": "Instagram",
    "vk.com": "VK",
    "facebook.com": "Facebook",
    "discord.gg": "Discord",
    "discord.com": "Discord",
    "tiktok.com": "TikTok",
    "weibo.com": "Weibo",
    "bilibili.com": "Bilibili",
    "afreecatv.com": "AfreecaTV",
    "douyu.com": "DouYu",
}


def map_social_platform(href: str, text: str) -> str | None:
    """Map social media URL and text to platform name.

    Args:
        href: The URL from the anchor tag.
        text: The link text from the anchor tag.

    Returns:
        str | None: The platform name (e.g., ``'Twitch'``, ``'YouTube'``),
        or ``None`` if it could not be determined.

    """
    parsed = urlparse(href)
    domain = parsed.netloc.lower()
    text_clean = text.strip()

    for key, platform in _PLATFORM_DOMAINS.items():
        if key in domain:
            return platform

    if "." in text_clean and not text_clean.startswith("@"):
        return "Official Website"
    if text_clean.startswith("@"):
        return text_clean[1:]
    return text_clean or None
