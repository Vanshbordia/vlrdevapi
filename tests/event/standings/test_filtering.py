from unittest.mock import patch

from selectolax.parser import HTMLParser

from vlrdevapi._base import SyncNamespace
from vlrdevapi._event._common import _filter_stages
from vlrdevapi._event.standings.parser import parse_subnav, parse_standings

_SUBNAV_HTML = """\
<html><body>
<nav class="wf-subnav">
  <a class="wf-subnav-item" href="/event/2283/valorant-champions-2025/standings/group/group-stage">
    <div class="wf-subnav-item-title">Group Stage</div>
    <div class="ge-text-light">Jan 15–Feb 5</div>
  </a>
  <a class="wf-subnav-item" href="/event/2283/valorant-champions-2025/standings/playoffs">
    <div class="wf-subnav-item-title">Playoffs</div>
    <div class="ge-text-light">Feb 8–Feb 15</div>
  </a>
</nav>
</body></html>
"""

_STAGE_HTML = """\
<html><body>
<div class="wf-label mod-large">Prize Distribution</div>
<div class="wf-ptable--standings">
  <div class="row">
    <div class="cell">Place</div>
    <div class="cell">Prize</div>
    <div class="cell">Team</div>
    <div class="cell">Points</div>
  </div>
  <div class="row">
    <div class="cell">1st</div>
    <div class="cell">$100,000</div>
    <div class="cell">
      <a href="/team/2/sentinels">
        <span class="text-of">Sentinels</span>
        <span class="ge-text-light">USA</span>
      </a>
    </div>
    <div class="cell">+100</div>
  </div>
  <div class="row">
    <div class="cell">2nd</div>
    <div class="cell">$50,000</div>
    <div class="cell">
      <a href="/team/120/100-thieves">
        <span class="text-of">100 Thieves</span>
        <span class="ge-text-light">USA</span>
      </a>
    </div>
    <div class="cell">+50</div>
  </div>
</div>
</body></html>
"""

_NO_SUBNAV_HTML = """\
<html><body>
<div class="wf-label mod-large">Prize Distribution</div>
<div class="wf-ptable--standings">
  <div class="row">
    <div class="cell">Place</div>
    <div class="cell">Prize</div>
    <div class="cell">Team</div>
  </div>
  <div class="row">
    <div class="cell">1st</div>
    <div class="cell">$25,000</div>
    <div class="cell">
      <a href="/team/120/100-thieves">
        <span class="text-of">100 Thieves</span>
        <span class="ge-text-light">USA</span>
      </a>
    </div>
  </div>
</div>
</body></html>
"""


def test_standings_filtering():
    """Test that standings filtering works with subnav-based event."""
    subnav_parser = HTMLParser(_SUBNAV_HTML)
    stage_parser = HTMLParser(_STAGE_HTML)

    with patch.object(SyncNamespace, "_fetch", return_value=subnav_parser):
        with patch.object(SyncNamespace, "_parallel_fetch", return_value=[stage_parser, stage_parser]):
            import vlrdevapi

            all_stages = vlrdevapi.event.standings(2283)
            assert len(all_stages) > 1

            # Filter by playoffs
            playoffs = vlrdevapi.event.standings(2283, stage="playoffs")
            assert len(playoffs) == 1
            assert "playoffs" in playoffs[0].stage_path.lower() or "playoffs" in playoffs[0].stage_name.lower()

            # Filter by group stage
            groups = vlrdevapi.event.standings(2283, stage="group-stage")
            assert len(groups) == 1
            assert "group-stage" in groups[0].stage_path.lower() or "group" in groups[0].stage_name.lower()


def test_standings_no_subnav():
    """Test standings parsing for an event without subnav."""
    no_subnav_parser = HTMLParser(_NO_SUBNAV_HTML)

    with patch.object(SyncNamespace, "_fetch", return_value=no_subnav_parser):
        import vlrdevapi
        standings = vlrdevapi.event.standings(2682)

    assert len(standings) > 0


def test_parse_subnav_returns_stage_links():
    """Test that parse_subnav correctly extracts (href, name) pairs."""
    parser = HTMLParser(_SUBNAV_HTML)
    stages = parse_subnav(parser)

    assert len(stages) == 2
    assert any("group-stage" in href for href, _ in stages)
    assert any("playoffs" in href for href, _ in stages)
    assert any("Group Stage" in name for _, name in stages)
    assert any("Playoffs" in name for _, name in stages)


def test_filter_stages_playoffs():
    """Test _filter_stages with 'playoffs' filter."""
    stages = [
        ("/event/2283/standings/group/group-stage", "Group Stage"),
        ("/event/2283/standings/playoffs", "Playoffs"),
    ]
    filtered = _filter_stages(stages, "playoffs")
    assert len(filtered) == 1
    assert "playoffs" in filtered[0][0]


def test_filter_stages_group():
    """Test _filter_stages with 'group-stage' filter."""
    stages = [
        ("/event/2283/standings/group/group-stage", "Group Stage"),
        ("/event/2283/standings/playoffs", "Playoffs"),
    ]
    filtered = _filter_stages(stages, "group-stage")
    assert len(filtered) == 1
    assert "group-stage" in filtered[0][0]


def test_filter_stages_none():
    """Test _filter_stages with no filter returns all stages."""
    stages = [
        ("/event/2283/standings/group/group-stage", "Group Stage"),
        ("/event/2283/standings/playoffs", "Playoffs"),
    ]
    filtered = _filter_stages(stages, None)
    assert len(filtered) == 2


def test_parse_standings_returns_entries():
    """Test that parse_standings extracts StandingEntry objects."""
    parser = HTMLParser(_STAGE_HTML)
    entries = parse_standings(parser)

    assert len(entries) == 2
    assert entries[0].place == "1st"
    assert entries[0].team.name == "Sentinels"
    assert entries[1].place == "2nd"
    assert entries[1].team.name == "100 Thieves"
