from datetime import date, datetime, time, timezone

import pytest

from selectolax.parser import HTMLParser
from zoneinfo import ZoneInfo

from tests.conftest import FIXTURES_DIR
from vlrdevapi.commons.datetime import parse_vlr_datetime
from vlrdevapi._player.matches.parser import parse_player_matches, _split_stage_bracket


_FIXTURES = FIXTURES_DIR / "player"


def _load_html(player_dir: str, filename: str) -> HTMLParser:
    path = _FIXTURES / player_dir / filename
    return HTMLParser(path.read_text(encoding="utf-8"))


class TestParseVlrDatetime:
    def test_explicit_source_tz(self):
        et = ZoneInfo("America/New_York")
        result = parse_vlr_datetime("2026/03/14", "10:30 pm", source_tz=et)
        assert result is not None
        assert result.tzinfo == timezone.utc
        assert result == datetime(2026, 3, 15, 2, 30, tzinfo=timezone.utc)

    def test_default_uses_vlr_timezone(self):
        result = parse_vlr_datetime("2026/03/14", "10:30 pm")
        assert result is not None
        assert result.tzinfo == timezone.utc
        et = ZoneInfo("America/New_York")
        expected = datetime(2026, 3, 14, 22, 30, tzinfo=et).astimezone(
            timezone.utc
        )
        assert result == expected

    def test_no_time(self):
        et = ZoneInfo("America/New_York")
        result = parse_vlr_datetime("2026/03/14", "", source_tz=et)
        expected = datetime(2026, 3, 14, 0, 0, tzinfo=et).astimezone(timezone.utc)
        assert result == expected

    def test_none_on_bad_date(self):
        result = parse_vlr_datetime("bad", "10:30 pm")
        assert result is None


class TestSplitStageBracket:
    def test_with_sdot(self):
        stage, bracket = _split_stage_bracket("Playoffs \u22c5 LBF")
        assert stage == "Playoffs"
        assert bracket == "LBF"

    def test_without_sdot(self):
        stage, bracket = _split_stage_bracket("LBF")
        assert stage == ""
        assert bracket == "LBF"

    def test_empty(self):
        stage, bracket = _split_stage_bracket("")
        assert stage == ""
        assert bracket == ""

    def test_sdot_no_bracket(self):
        stage, bracket = _split_stage_bracket("Playoffs \u22c5 ")
        assert stage == "Playoffs"
        assert bracket == ""


class _TestParseBase:
    """Shared structural invariants for any player match history page."""

    def test_has_next_page(self):
        assert isinstance(self.page.has_next_page, bool)

    def test_match_count(self):
        assert len(self.page.matches) > 0

    def test_all_matches_have_valid_ids_and_urls(self):
        for m in self.page.matches:
            assert m.match_id > 0
            assert m.url.startswith("/")
            assert str(m.match_id) in m.url

    def test_all_matches_have_events(self):
        for m in self.page.matches:
            assert m.event != ""

    def test_all_matches_have_team_data(self):
        for m in self.page.matches:
            assert m.team1.name != ""
            assert m.team2.name != ""

    def test_all_matches_have_valid_scores_and_results(self):
        for m in self.page.matches:
            assert m.score1 >= 0
            assert m.score2 >= 0
            assert m.result in ("", "win", "loss")
            if m.result == "win":
                assert m.score1 >= m.score2
            elif m.result == "loss":
                assert m.score2 >= m.score1

    def test_all_matches_have_valid_dates(self):
        for m in self.page.matches:
            if m.date is not None:
                assert isinstance(m.date, date)
            if m.time is not None:
                assert isinstance(m.time, time)
            if m.datetime is not None:
                assert isinstance(m.datetime, datetime)
                assert m.datetime.tzinfo == timezone.utc

    def test_stage_and_bracket_are_strings(self):
        for m in self.page.matches:
            assert isinstance(m.stage, str)
            assert isinstance(m.bracket, str)


class TestParseEthanPage1(_TestParseBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.page = parse_player_matches(_load_html("11225_ethan", "matches.html"))


class TestParseEthanPage2(_TestParseBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.page = parse_player_matches(
            _load_html("11225_ethan", "matches_page2.html")
        )

