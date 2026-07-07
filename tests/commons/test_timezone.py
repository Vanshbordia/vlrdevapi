from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from selectolax.parser import HTMLParser

from vlrdevapi.commons.timezone import (
    VLR_STORED_TZ,
    detect_vlr_timezone,
    parse_vlr_stored_datetime,
)

_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "test_html"
    / "matches"
    / "reference_match_timezone.html"
)


@pytest.fixture
def reference_html() -> HTMLParser | None:
    if not _FIXTURE.exists():
        pytest.skip(f"Fixture not found: {_FIXTURE}")
    return HTMLParser(_FIXTURE.read_text(encoding="utf-8"))


class TestParseVlrStoredDatetime:
    def test_converts_eastern_to_utc(self):
        result = parse_vlr_stored_datetime("2026-06-21 10:20:00")
        assert result == datetime(2026, 6, 21, 14, 20, tzinfo=UTC)

    def test_none_on_empty(self):
        assert parse_vlr_stored_datetime("") is None


class TestDetectVlrTimezone:
    def test_detects_ist_from_reference_match(self, reference_html):
        zone = detect_vlr_timezone(reference_html)
        assert str(zone) == "Asia/Kolkata"

    def test_detects_ist_from_inline_html(self):
        html = HTMLParser(
            """
            <div class="match-header-date">
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="dddd, MMMM D">Sunday, June 21</div>
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="h:mm A z">7:50 PM IST</div>
            </div>
            """
        )
        zone = detect_vlr_timezone(html)
        assert zone == ZoneInfo("Asia/Kolkata")

    def test_offset_fallback_for_unknown_abbrev(self):
        html = HTMLParser(
            """
            <div class="match-header-date">
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="dddd, MMMM D">Sunday, June 21</div>
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="h:mm A z">7:50 PM IST</div>
            </div>
            """
        )
        zone = detect_vlr_timezone(html)
        stored = parse_vlr_stored_datetime("2026-06-21 10:20:00")
        local = datetime(2026, 6, 21, 19, 50, tzinfo=zone)
        assert local.astimezone(UTC) == stored