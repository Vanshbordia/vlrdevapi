"""Shared parsing utilities for series (private module)."""

from __future__ import annotations

import re
from bs4 import BeautifulSoup

from .models import MapAction
from ..config import get_config
from ..fetcher import batch_fetch_html
from ..utils import extract_text

_config = get_config()

# Pre-compiled regex patterns for performance
_WHITESPACE_RE = re.compile(r"\s+")
_PICKS_BANS_RE = re.compile(r"([^;]+?)\s+(ban|pick)\s+([^;]+?)(?:;|$)", re.IGNORECASE)
_REMAINS_RE = re.compile(r"([^;]+?)\s+remains\b", re.IGNORECASE)
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)\s*([A-Z]{2,4}|[+\-]\d{2})?", re.IGNORECASE)
_MAP_NUMBER_RE = re.compile(r"^\s*\d+\s*")

_METHOD_LABELS: dict[str, str] = {
    "elim": "Elimination",
    "elimination": "Elimination",
    "defuse": "SpikeDefused",
    "defused": "SpikeDefused",
    "boom": "SpikeExplosion",
    "explode": "SpikeExplosion",
    "explosion": "SpikeExplosion",
    "time": "TimeRunOut",
    "timer": "TimeRunOut",
}


def _fetch_team_meta_batch(team_ids: list[int], timeout: float) -> dict[int, tuple[str | None, str | None, str | None]]:
    """Fetch team metadata for multiple teams concurrently.
    
    Args:
        team_ids: List of team IDs
        timeout: Request timeout
    
    Returns:
        Dictionary mapping team_id to (short_tag, country, country_code)
    """
    if not team_ids:
        return {}
    
    # Build URLs for all teams
    urls = [f"{_config.vlr_base}/team/{team_id}" for team_id in team_ids]
    
    # Batch fetch all team pages concurrently
    batch_results = batch_fetch_html(urls, timeout=timeout, max_workers=min(2, len(urls)))
    
    # Parse metadata from each page
    results: dict[int, tuple[str | None, str | None, str | None]] = {}
    
    for team_id, url in zip(team_ids, urls):
        html = batch_results.get(url)
        
        if isinstance(html, Exception) or not html:
            results[team_id] = (None, None, None)
            continue
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            short_tag = extract_text(soup.select_one(".team-header .team-header-tag"))
            country_el = soup.select_one(".team-header .team-header-country")
            country = extract_text(country_el) if country_el else None
            
            flag = None
            if country_el:
                flag_icon = country_el.select_one(".flag")
                if flag_icon:
                    classes_val = flag_icon.get("class")
                    flag_classes: list[str] = [str(c) for c in classes_val] if isinstance(classes_val, (list, tuple)) else []
                    for cls in flag_classes:
                        if cls.startswith("mod-") and cls != "mod-dark":
                            flag = cls.removeprefix("mod-")
                            break
            
            results[team_id] = (short_tag or None, country, flag)
        except Exception:
            results[team_id] = (None, None, None)
    
    return results


def _parse_note_for_picks_bans(
    note_text: str,
    team1_aliases: list[str],
    team2_aliases: list[str],
) -> tuple[list[MapAction], list[MapAction], list[MapAction], str | None]:
    """Parse picks/bans from header note text."""
    text = _WHITESPACE_RE.sub(" ", note_text).strip()
    picks: list[MapAction] = []
    bans: list[MapAction] = []
    remaining: str | None = None
    
    def normalize_team(who: str) -> str:
        who_clean = who.strip()
        for aliases in (team1_aliases, team2_aliases):
            for alias in aliases:
                if alias and alias.lower() in who_clean.lower():
                    return aliases[0]
        return who_clean
    
    ordered_actions: list[MapAction] = []
    for m in _PICKS_BANS_RE.finditer(text):
        who = m.group(1).strip()
        action = m.group(2).lower()
        game_map = m.group(3).strip()
        canonical = normalize_team(who)
        map_action = MapAction(action=action, team=canonical, map=game_map)
        ordered_actions.append(map_action)
        if action == "ban":
            bans.append(map_action)
        else:
            picks.append(map_action)
    
    rem_m = _REMAINS_RE.search(text)
    if rem_m:
        remaining = rem_m.group(1).strip()
    
    return ordered_actions, picks, bans, remaining
