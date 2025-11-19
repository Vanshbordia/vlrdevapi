"""Event match summary functionality."""

from __future__ import annotations

import datetime
from bs4 import BeautifulSoup

from .models import MatchSummary, StageMatches
from ..config import get_config
from ..fetcher import fetch_html
from ..exceptions import NetworkError
from ..utils import extract_text, parse_date

_config = get_config()


def match_summary(event_id: int, timeout: float | None = None) -> MatchSummary | None:
    """
    Get event match summary.
    
    Args:
        event_id: Event ID
        timeout: Request timeout in seconds
    
    Returns:
        Match summary or None if not found
    
    Example:
        >>> import vlrdevapi as vlr
        >>> summary = vlr.events.match_summary(event_id=123)
        >>> print(f"Total: {summary.total_matches}, Completed: {summary.completed}")
    """
    url = f"{_config.vlr_base}/event/matches/{event_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    
    # Count matches and organize by stage
    total = 0
    completed = 0
    upcoming = 0
    ongoing = 0
    
    # Track stage-level statistics
    stage_stats: dict[str, dict] = {}
    
    for card in soup.select("a.match-item"):
        total += 1
        
        # Parse status
        ml = card.select_one(".match-item-eta .ml")
        match_status = "upcoming"
        if ml:
            classes_raw = ml.get("class")
            classes: list[str] = []
            if isinstance(classes_raw, list):
                classes = classes_raw
            elif isinstance(classes_raw, str):
                classes = [classes_raw]
            classes_list = classes
            if any("mod-completed" in str(c) for c in classes_list):
                completed += 1
                match_status = "completed"
            elif any("mod-live" in str(c) or "mod-ongoing" in str(c) for c in classes_list):
                ongoing += 1
                match_status = "ongoing"
            else:
                upcoming += 1
        else:
            upcoming += 1
        
        # Parse stage name
        event_el = card.select_one(".match-item-event")
        stage_name = extract_text(event_el) or "Unknown Stage"
        
        # Remove phase from stage name if present
        series_el = card.select_one(".match-item-event-series")
        phase = extract_text(series_el) or None
        if phase and stage_name:
            stage_name = stage_name.replace(phase, "").strip()
        
        # Parse date
        match_date: datetime.date | None = None
        label = card.find_previous("div", class_="wf-label mod-large")
        if label:
            texts = [frag.strip() for frag in label.find_all(string=True, recursive=False)]
            text = " ".join(t for t in texts if t)
            match_date = parse_date(text, ["%a, %B %d, %Y", "%A, %B %d, %Y", "%B %d, %Y"])
        
        # Initialize stage stats if not exists
        if stage_name not in stage_stats:
            stage_stats[stage_name] = {
                "count": 0,
                "completed": 0,
                "upcoming": 0,
                "ongoing": 0,
                "dates": []
            }
        
        # Update stage stats
        stage_stats[stage_name]["count"] += 1
        if match_status == "completed":
            stage_stats[stage_name]["completed"] += 1
        elif match_status == "ongoing":
            stage_stats[stage_name]["ongoing"] += 1
        else:
            stage_stats[stage_name]["upcoming"] += 1
        
        if match_date:
            stage_stats[stage_name]["dates"].append(match_date)
    
    # Build stage summaries
    stages: list[StageMatches] = []
    for stage_name, stats in stage_stats.items():
        dates = stats["dates"]
        start_date = min(dates) if dates else None
        end_date = max(dates) if dates else None
        
        stages.append(StageMatches(
            name=stage_name,
            match_count=stats["count"],
            completed=stats["completed"],
            upcoming=stats["upcoming"],
            ongoing=stats["ongoing"],
            start_date=start_date,
            end_date=end_date,
        ))
    
    return MatchSummary(
        event_id=event_id,
        total_matches=total,
        completed=completed,
        upcoming=upcoming,
        ongoing=ongoing,
        stages=stages,
    )
