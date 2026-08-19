import pytest

from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._series.economy.parser import parse_economy_data


_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "542272_nrg-vs-fnatic-valorant-champions-2025-gf"
)


def _load_html(filename: str) -> HTMLParser:
    if _LIVE:
        series_id = _FIXTURES.name.split("_")[0]
        game_id = filename.split("_")[1]
        url = f"/{series_id}/?game={game_id}&tab=economy"
        return HTMLParser(live_fetch(url))
    path = _FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseEconomyGame:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_html("game_233478_economy.html")
        self.game1 = parse_economy_data(self.html, game_id=1)
        self.game2 = parse_economy_data(self.html, game_id=2)

    def test_game_one_rounds(self):
        assert len(self.game1.rounds) == 16
        assert self.game1.team1 == "NRG"
        assert self.game1.team2 == "FNC"

    def test_game_one_first_round(self):
        round_1 = self.game1.rounds[0]
        assert round_1.round_number == 1
        assert round_1.spent_team1 == 3650
        assert round_1.spent_team2 == 3600

    def test_game_two_differs_from_game_one(self):
        assert len(self.game1.rounds) == 16
        assert len(self.game2.rounds) == 19
        round_1 = self.game2.rounds[0]
        assert round_1.spent_team1 == 3750
        assert round_1.spent_team2 == 3350

    def test_positional_game_one_matches_real_id(self):
        real = parse_economy_data(self.html, game_id="233478")
        assert len(real.rounds) == len(self.game1.rounds) == 16
        assert [r.spent_team1 for r in real.rounds] == [
            r.spent_team1 for r in self.game1.rounds
        ]


_BO1_VETO_FIXTURES = FIXTURES_DIR / "series" / "64819"


def _load_bo1_veto_html(filename: str) -> HTMLParser:
    path = _BO1_VETO_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseEconomyBo1WithDeciderVeto:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_bo1_veto_html("game_65212_economy.html")
        self.result = parse_economy_data(self.html, game_id=1)

    def test_teams(self):
        assert self.result.team1 == "MAD"
        assert self.result.team2 == "HZ"

    def test_rounds_exist(self):
        assert len(self.result.rounds) > 0

    def test_first_round(self):
        round_1 = self.result.rounds[0]
        assert round_1.round_number == 1
        assert isinstance(round_1.spent_team1, int)
        assert isinstance(round_1.spent_team2, int)

    def test_positional_matches_real_id(self):
        real = parse_economy_data(self.html, game_id="65212")
        assert len(real.rounds) == len(self.result.rounds)
        assert [r.spent_team1 for r in real.rounds] == [
            r.spent_team1 for r in self.result.rounds
        ]


_BO1_PICK_FIXTURES = FIXTURES_DIR / "series" / "30788"


def _load_bo1_pick_html(filename: str) -> HTMLParser:
    path = _BO1_PICK_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseEconomyBo1WithPickVeto:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_bo1_pick_html("game_47971_economy.html")
        self.result = parse_economy_data(self.html, game_id=1)

    def test_teams(self):
        assert self.result.team1 == "CNL"
        assert self.result.team2 == "NXLGA"

    def test_rounds_exist(self):
        assert len(self.result.rounds) > 0

    def test_first_round(self):
        round_1 = self.result.rounds[0]
        assert round_1.round_number == 1
        assert isinstance(round_1.spent_team1, int)
        assert isinstance(round_1.spent_team2, int)

    def test_positional_matches_real_id(self):
        real = parse_economy_data(self.html, game_id="47971")
        assert len(real.rounds) == len(self.result.rounds)
        assert [r.spent_team1 for r in real.rounds] == [
            r.spent_team1 for r in self.result.rounds
        ]
