from selectolax.parser import HTMLParser

from vlrdevapi._event.stages.parser import parse_event_stages
from vlrdevapi._event.stages.models import EventStages

_SYNTHETIC_STAGES_HTML = """\
<html>
<body>
<div class="zx-subnav zx-subnav--filter">
  <div class="zx-opt-row">
    <div class="zx-label">Stage:</div>
    <a class="opt" href="/event/matches/2860/?series_id=1234&amp;group=all"><div>Group Stage</div></a>
    <a class="opt" href="/event/matches/2860/?series_id=5678&amp;group=all"><div>Playoffs</div></a>
  </div>
</div>
</body>
</html>
"""


class TestParseEventStages:
    """Test parsing of event stages from HTML."""

    def test_parse_event_stages_with_data(self):
        """Test parsing stages when data is present."""
        html = HTMLParser(_SYNTHETIC_STAGES_HTML)
        result = parse_event_stages(html, 2860)

        assert result is not None
        assert isinstance(result, EventStages)
        assert len(result.stages) >= 2

        # Check stage names and IDs
        stage_names = [s.name for s in result.stages]
        assert "Playoffs" in stage_names
        assert "Group Stage" in stage_names

        # Check IDs are strings
        for stage in result.stages:
            assert isinstance(stage.id, str)
            assert stage.id.isdigit()  # Should be numeric strings

    def test_parse_event_stages_no_stages(self):
        """Test parsing when no stages section exists."""
        # Create minimal HTML without stages section
        html = HTMLParser("<html><body><div>No stages here</div></body></html>")
        result = parse_event_stages(html, 12345)

        assert isinstance(result, EventStages)
        assert len(result.stages) == 0
