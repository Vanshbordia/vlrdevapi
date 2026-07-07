from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from selectolax.parser import HTMLParser

from vlrdevapi.commons.timezone import (
    _TIME_WITH_TZ_RE,
    _zone_from_abbrev,
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
    def test_detects_timezone_consistent_with_reference_fixture(self, reference_html):
        zone = detect_vlr_timezone(reference_html)
        time_el = reference_html.css_first(
            ".moment-tz-convert[data-moment-format='h:mm A z']",
        )
        date_el = reference_html.css_first(
            ".moment-tz-convert[data-moment-format='dddd, MMMM D']",
        )
        ts_el = reference_html.css_first(".moment-tz-convert[data-utc-ts]")
        assert time_el is not None
        assert ts_el is not None
        assert date_el is not None

        displayed_time = time_el.text(strip=True)
        stored = parse_vlr_stored_datetime(ts_el.attributes.get("data-utc-ts", ""))
        assert stored is not None

        abbrev_match = _TIME_WITH_TZ_RE.match(displayed_time)
        if abbrev_match:
            expected = _zone_from_abbrev(abbrev_match.group("tz"))
            assert expected is not None
            assert zone == expected

        time_match = _TIME_WITH_TZ_RE.match(displayed_time)
        assert time_match is not None
        local_time = datetime.strptime(
            time_match.group("time").upper(),
            "%I:%M %p",
        ).time()
        partial_date = datetime.strptime(
            date_el.text(strip=True),
            "%A, %B %d",
        )
        local_date = partial_date.replace(year=stored.year).date()
        localized = datetime.combine(local_date, local_time, tzinfo=zone)
        assert localized.astimezone(UTC) == stored

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

    def test_detects_eastern_from_inline_html(self):
        html = HTMLParser(
            """
            <div class="match-header-date">
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="dddd, MMMM D">Sunday, June 21</div>
              <div class="moment-tz-convert" data-utc-ts="2026-06-21 10:20:00"
                   data-moment-format="h:mm A z">10:20 AM ET</div>
            </div>
            """
        )
        zone = detect_vlr_timezone(html)
        assert zone == ZoneInfo("America/New_York")