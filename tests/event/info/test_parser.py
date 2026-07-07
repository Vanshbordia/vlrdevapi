from datetime import datetime, timezone

import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from tests.helpers.fixtures import expected_event_dates
from vlrdevapi._event.info.parser import parse_event_info


def _load_event_html(event_id: int, slug: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/event/{event_id}"))
    path = FIXTURES_DIR / "event" / f"{event_id}_{slug}" / "overview.html"
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseEventInfoVCTEMEA:
    """VCT 2026: EMEA Stage 1 — full breadcrumb, TBD prize, location with venue."""

    def setup_method(self):
        self.html = _load_event_html(2863, "vct-2026-emea-stage-1")
        self.result = parse_event_info(self.html, 2863)

    def test_id(self):
        assert self.result.id == 2863

    def test_name(self):
        assert self.result.name == "VCT 2026: EMEA Stage 1"

    def test_subtitle(self):
        assert self.result.subtitle == (
            "Part of the Valorant Champions Tour, Riot's official 2026 tournament circuit."
        )

    def test_image_url(self):
        assert self.result.image_url == "https://owcdn.net/img/65ab59620a233.png"

    def test_series(self):
        assert self.result.series is not None
        assert self.result.series.name == "Valorant Champions Tour 2026"
        assert self.result.series.href == "/vct"

    def test_stage(self):
        assert self.result.stage is not None
        assert self.result.stage.name == "Stage 1"
        assert self.result.stage.href == "/vct/?stage=1"

    def test_regions(self):
        assert len(self.result.regions) == 1
        assert self.result.regions[0].name == "EMEA"
        assert self.result.regions[0].href == "/vct/?region=27"

    def test_dates(self):
        expected_start, expected_end = expected_event_dates(self.html)
        assert self.result.start_date == expected_start
        assert self.result.end_date == expected_end
        assert self.result.start_date is not None
        assert self.result.end_date is not None
        assert self.result.start_date.year == 2026
        assert self.result.start_date.month == 4

    def test_prize_tbd(self):
        assert self.result.prize is not None
        assert self.result.prize.is_tbd is True
        assert self.result.prize.amount is None
        assert self.result.prize.currency_symbol is None
        assert self.result.prize.currency_code is None

    def test_location(self):
        assert self.result.location is not None
        assert self.result.location.country == "Germany"
        assert self.result.location.venue == "Riot Games Arena, Berlin"

    def test_region_location_none(self):
        assert self.result.region_location is None


class TestParseEventInfoGAMEON:
    """GAMEON Productivity and Technology Tournament 2026 — converted currency prize, no breadcrumb."""

    def setup_method(self):
        self.html = _load_event_html(
            2949, "gameon-productivity-and-technology-tournament-2026"
        )
        self.result = parse_event_info(self.html, 2949)

    def test_id(self):
        assert self.result.id == 2949

    def test_name(self):
        assert self.result.name == "GAMEON Productivity and Technology Tournament 2026"

    def test_subtitle(self):
        assert self.result.subtitle == ""

    def test_image_url(self):
        assert self.result.image_url.startswith("https://")

    def test_series_none(self):
        assert self.result.series is None

    def test_stage_none(self):
        assert self.result.stage is None

    def test_regions_empty(self):
        assert self.result.regions == []

    def test_dates_short_format(self):
        expected_start, expected_end = expected_event_dates(self.html)
        assert self.result.start_date == expected_start
        assert self.result.end_date == expected_end
        assert self.result.start_date is not None
        assert self.result.end_date is not None
        assert self.result.start_date.year == 2026
        assert self.result.start_date.month == 4

    def test_prize_with_conversion(self):
        assert self.result.prize is not None
        assert self.result.prize.is_tbd is False
        assert self.result.prize.amount == 600000
        assert self.result.prize.converted_amount == 13403

    def test_location(self):
        assert self.result.location is not None
        assert self.result.location.country == "Turkey"
        assert self.result.location.venue == "Ankara"


class TestParseEventInfoChallengersJapan:
    """Challengers 2026: Japan Split 1 — JPY prize with USD conversion, region flag-only."""

    def setup_method(self):
        html = _load_event_html(2847, "challengers-2026-japan-split-1")
        self.result = parse_event_info(html, 2847)

    def test_id(self):
        assert self.result.id == 2847

    def test_name(self):
        assert self.result.name == "Challengers 2026: Japan Split 1"

    def test_subtitle(self):
        assert "Valorant Champions Tour" in self.result.subtitle

    def test_series(self):
        assert self.result.series is not None
        assert "Valorant Challengers League 2026" in self.result.series.name

    def test_dates(self):
        assert self.result.start_date is not None
        assert self.result.end_date is not None
        assert self.result.start_date.year == 2026
        assert self.result.start_date.month == 2
        assert self.result.end_date.month == 4

    def test_prize_jpy(self):
        assert self.result.prize is not None
        assert self.result.prize.is_tbd is False
        assert self.result.prize.amount == 4000000
        assert self.result.prize.currency_code == "JPY"
        assert self.result.prize.converted_amount == 25656

    def test_region_location_flag_only(self):
        assert self.result.region_location is not None
        assert self.result.region_location.country == "Japan"
        assert self.result.region_location.venue == ""

    def test_location_none(self):
        assert self.result.location is None


class TestParseEventInfo100TCashApp:
    """100T x Cashapp Gamers for Equality — single day, $0 prize, region flag-only."""

    def setup_method(self):
        html = _load_event_html(58, "100t-x-cashapp-gamers-for-equality")
        self.result = parse_event_info(html, 58)

    def test_id(self):
        assert self.result.id == 58

    def test_name(self):
        assert self.result.name == "100T x Cashapp Gamers for Equality"

    def test_subtitle(self):
        assert self.result.subtitle == ""

    def test_series_none(self):
        assert self.result.series is None

    def test_single_day_date(self):
        assert self.result.start_date is not None
        assert self.result.end_date is not None
        assert self.result.start_date == self.result.end_date
        assert self.result.start_date.year == 2020
        assert self.result.start_date.month == 7
        assert self.result.start_date.day == 8

    def test_prize_zero_usd(self):
        assert self.result.prize is not None
        assert self.result.prize.is_tbd is False
        assert self.result.prize.amount == 0
        assert self.result.prize.currency_symbol == "$"
        assert self.result.prize.currency_code == "USD"

    def test_region_location(self):
        assert self.result.region_location is not None
        assert self.result.region_location.country == "United States"

    def test_location_none(self):
        assert self.result.location is None


class TestParseEventInfoVCTAmericas:
    """VCT 2026: Americas Kickoff — full breadcrumb, location with venue."""

    def setup_method(self):
        html = _load_event_html(2682, "vct-2026-americas-kickoff")
        self.result = parse_event_info(html, 2682)

    def test_id(self):
        assert self.result.id == 2682

    def test_name(self):
        assert self.result.name == "VCT 2026: Americas Kickoff"

    def test_series(self):
        assert self.result.series is not None
        assert self.result.series.name == "Valorant Champions Tour 2026"
        assert self.result.series.href == "/vct"

    def test_stage(self):
        assert self.result.stage is not None
        assert self.result.stage.name == "Kickoff"

    def test_regions(self):
        assert len(self.result.regions) == 1
        assert self.result.regions[0].name == "Americas"

    def test_dates(self):
        assert self.result.start_date is not None
        assert self.result.end_date is not None
        assert self.result.start_date.year == 2026
        assert self.result.start_date.month == 1
        assert self.result.end_date.month == 2

    def test_prize_zero_usd(self):
        assert self.result.prize is not None
        assert self.result.prize.amount == 0
        assert self.result.prize.currency_code == "USD"

    def test_location(self):
        assert self.result.location is not None
        assert self.result.location.country == "United States"
        assert "Los Angeles" in self.result.location.venue

