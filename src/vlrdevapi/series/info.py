"""Series information functionality."""

from __future__ import annotations

import datetime
from bs4 import BeautifulSoup

from .models import Info, TeamInfo
from ._parser import _fetch_team_meta_batch, _parse_note_for_picks_bans, _WHITESPACE_RE, _TIME_RE
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, extract_id_from_url

_config = get_config()


def info(match_id: int, timeout: float | None = None) -> Info | None:
    """
    Get series information.
    
    Args:
        match_id: Match ID
        timeout: Request timeout in seconds
    
    Returns:
        Series information or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> info = vlr.series.info(match_id=12345)
        >>> print(f"{info.teams[0].name} vs {info.teams[1].name}")
        >>> print(f"Score: {info.score[0]}-{info.score[1]}")
    """
    url = f"{_config.vlr_base}/{match_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    header = soup.select_one(".wf-card.match-header")
    if not header:
        return None
    
    # Event name and phase
    event_name = extract_text(header.select_one(".match-header-event div[style*='font-weight']")) or \
                 extract_text(header.select_one(".match-header-event .wf-title-med"))
    event_phase = _WHITESPACE_RE.sub(" ", extract_text(header.select_one(".match-header-event-series"))).strip()
    
    # Date, time, and patch information
    date_el = header.select_one(".match-header-date .moment-tz-convert")
    match_date: datetime.date | None = None
    time_value: datetime.time | None = None
    patch_text: str | None = None
    
    if date_el and date_el.has_attr("data-utc-ts"):
        try:
            dt_attr = date_el.get("data-utc-ts")
            dt_str = dt_attr if isinstance(dt_attr, str) else None
            if dt_str:
                dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                match_date = dt.date()
        except Exception:
            pass
    
    time_els = header.select(".match-header-date .moment-tz-convert")
    if len(time_els) >= 2:
        time_node = time_els[1]
        dt_attr = time_node.get("data-utc-ts")
        dt_str = dt_attr if isinstance(dt_attr, str) else None
        if dt_str:
            try:
                dt_parsed = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                tz_utc = datetime.timezone.utc
                time_value = datetime.time(hour=dt_parsed.hour, minute=dt_parsed.minute, tzinfo=tz_utc)
            except Exception:
                pass
        if time_value is None:
            raw = extract_text(time_node)
            # Handles formats like "2:00 PM PST" and "2:00 PM +02"
            m = _TIME_RE.match(raw)
            if m:
                hour = int(m.group(1)) % 12
                minute = int(m.group(2))
                if m.group(3).upper() == "PM":
                    hour += 12
                tzinfo = None
                suffix = m.group(4)
                if suffix and suffix.startswith(("+", "-")) and len(suffix) == 3:
                    sign = 1 if suffix[0] == "+" else -1
                    offset_hours = int(suffix[1:])
                    tzinfo = datetime.timezone(sign * datetime.timedelta(hours=offset_hours))
                else:
                    tzinfo = datetime.timezone.utc if dt_attr else None
                time_value = datetime.time(hour=hour, minute=minute, tzinfo=tzinfo)
    patch_el = header.select_one(".match-header-date div[style*='font-style: italic']")
    if patch_el:
        patch_text = extract_text(patch_el) or None
    
    # Teams and scores
    t1_link = header.select_one(".match-header-link.mod-1")
    t2_link = header.select_one(".match-header-link.mod-2")
    t1 = extract_text(header.select_one(".match-header-link.mod-1 .wf-title-med"))
    t2 = extract_text(header.select_one(".match-header-link.mod-2 .wf-title-med"))
    t1_href = t1_link.get("href") if t1_link else None
    t2_href = t2_link.get("href") if t2_link else None
    t1_href = t1_href if isinstance(t1_href, str) else None
    t2_href = t2_href if isinstance(t2_href, str) else None
    t1_id = extract_id_from_url(t1_href, "team")
    t2_id = extract_id_from_url(t2_href, "team")
    
    t1_short, t1_country, t1_country_code = None, None, None
    t2_short, t2_country, t2_country_code = None, None, None
    
    # Batch fetch team metadata for both teams concurrently
    team_ids_to_fetch = [tid for tid in [t1_id, t2_id] if tid is not None]
    if team_ids_to_fetch:
        team_meta_map = _fetch_team_meta_batch(team_ids_to_fetch, timeout)
        if t1_id:
            t1_short, t1_country, t1_country_code = team_meta_map.get(t1_id, (None, None, None))
        if t2_id:
            t2_short, t2_country, t2_country_code = team_meta_map.get(t2_id, (None, None, None))
    
    s1 = header.select_one(".match-header-vs-score-winner")
    s2 = header.select_one(".match-header-vs-score-loser")
    raw_score: tuple[int | None, int | None] = (None, None)
    try:
        if s1 and s2:
            raw_score = (int(extract_text(s1)), int(extract_text(s2)))
    except ValueError:
        pass
    
    notes = header.select(".match-header-vs-note")
    status_note = extract_text(notes[0]) if notes else ""
    best_of = extract_text(notes[1]) if len(notes) > 1 else None
    
    # Picks/bans
    team1_info = TeamInfo(
        id=t1_id,
        name=t1,
        short=t1_short,
        country=t1_country,
        country_code=t1_country_code,
        score=raw_score[0],
    )
    team2_info = TeamInfo(
        id=t2_id,
        name=t2,
        short=t2_short,
        country=t2_country,
        country_code=t2_country_code,
        score=raw_score[1],
    )
    
    header_note_node = header.select_one(".match-header-note")
    header_note_text = extract_text(header_note_node)
    
    aliases1 = [alias for alias in (team1_info.short, team1_info.name) if alias]
    aliases2 = [alias for alias in (team2_info.short, team2_info.name) if alias]
    
    map_actions, picks, bans, remaining = _parse_note_for_picks_bans(
        header_note_text,
        aliases1 or [team1_info.name],
        aliases2 or [team2_info.name],
    )
    
    return Info(
        match_id=match_id,
        teams=(team1_info, team2_info),
        score=raw_score,
        status_note=status_note.lower(),
        best_of=best_of,
        event=event_name,
        event_phase=event_phase,
        date=match_date,
        time=time_value,
        patch=patch_text,
        map_actions=map_actions,
        picks=picks,
        bans=bans,
        remaining=remaining,
    )
