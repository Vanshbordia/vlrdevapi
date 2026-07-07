from pathlib import Path

import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._event.matches.parser import parse_event_matches
from vlrdevapi._event.matches.models import MatchStatus

_FIXTURES_2863 = (
    FIXTURES_DIR
    / "event"
    / "2863_vct-2026-emea-stage-1"
)

_FIXTURES_2760 = (
    FIXTURES_DIR
    / "event"
    / "2760_valorant-masters-santiago-2026"
)


def _load_html(base: Path, filename: str) -> HTMLParser:
    return HTMLParser((base / filename).read_text(encoding="utf-8"))


class TestParseEventMatchesCompleted:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_event_matches(
            _load_html(_FIXTURES_2863, "matches_completed.html"), 2863
        )

    def test_event_id(self):
        assert self.result.event_id == 2863

    def test_has_matches(self):
        assert len(self.result.matches) > 0

    def test_all_completed(self):
        for m in self.result.matches:
            assert m.status == MatchStatus.COMPLETED

    def test_first_match_details(self):
        m = self.result.matches[0]
        assert m.match_id == 660386
        assert m.stage == "Playoffs"
        assert m.phase == "Grand Final"

    def test_completed_teams_have_scores(self):
        m = self.result.matches[0]
        assert len(m.teams) == 2
        assert m.teams[0].name == "Team Vitality"
        assert m.teams[0].score == 2
        assert m.teams[1].name == "Team Heretics"
        assert m.teams[1].score == 3

    def test_winner_detected(self):
        m = self.result.matches[0]
        assert m.teams[0].winner is False
        assert m.teams[1].winner is True

    def test_dates_parsed(self):
        first_date = self.result.matches[0].match_date
        assert first_date is not None
        assert first_date.year == 2026
        assert first_date.month == 5
        assert first_date.day == 17

    def test_time_parsed(self):
        first_time = self.result.matches[0].match_time
        assert first_time is not None

    def test_datetime_utc_populated(self):
        m = self.result.matches[0]
        if m.match_date and m.match_time:
            assert m.datetime_utc is not None

    def test_second_match_different_date(self):
        m = self.result.matches[1]
        assert m.match_id == 660392
        assert m.match_date is not None
        assert m.match_date.day == 16
        assert m.teams[0].name == "FUT Esports"
        assert m.teams[1].name == "Team Heretics"


class TestParseEventMatchesUpcoming:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_event_matches(
            _load_html(_FIXTURES_2863, "matches_upcoming.html"), 2863
        )

    def test_no_upcoming_matches_concluded(self):
        assert len(self.result.matches) == 0


class TestParseEventMatchesAll:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_event_matches(
            _load_html(_FIXTURES_2863, "matches_all.html"), 2863
        )

    def test_has_all_match_types(self):
        statuses = {m.status for m in self.result.matches}
        assert MatchStatus.COMPLETED in statuses

    def test_total_matches_more_than_filtered(self):
        completed = parse_event_matches(
            _load_html(_FIXTURES_2863, "matches_completed.html"), 2863
        )
        assert len(self.result.matches) >= len(completed.matches)


class TestParseEventMatchesCompleted2760:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_event_matches(
            _load_html(_FIXTURES_2760, "matches_all.html"), 2760
        )

    def test_event_id(self):
        assert self.result.event_id == 2760

    def test_has_matches(self):
        assert len(self.result.matches) > 0

    def test_all_completed(self):
        for m in self.result.matches:
            assert m.status == MatchStatus.COMPLETED

    def test_first_match(self):
        m = self.result.matches[0]
        assert m.match_id == 625788
        assert m.stage == "Swiss Stage"
        assert m.phase == "Round 1"
        assert m.teams[0].name == "Gentle Mates"
        assert m.teams[0].score == 2
        assert m.teams[0].winner is True
        assert m.teams[1].name == "EDward Gaming"
        assert m.teams[1].score == 0
        assert m.teams[1].winner is False

    def test_date_parsed(self):
        from datetime import date

        m = self.result.matches[0]
        assert m.match_date == date(2026, 2, 28)


class TestParseEventMatchesEmptyUpcoming:
    def test_no_upcoming_returns_empty(self):
        result = parse_event_matches(
            _load_html(_FIXTURES_2760, "matches_upcoming.html"), 2760
        )
        assert result.event_id == 2760
        assert result.matches == []


class TestParseEmptyHtml:
    def test_empty_html_returns_empty(self):
        html = HTMLParser("<html><body></body></html>")
        result = parse_event_matches(html, 99999)
        assert result.event_id == 99999
        assert result.matches == []

