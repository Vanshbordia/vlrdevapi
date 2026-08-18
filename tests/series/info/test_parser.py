import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._series.info.parser import parse_series_info

_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "542272_nrg-vs-fnatic-valorant-champions-2025-gf"
)

def _load_html(filename: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/{_FIXTURES.name.split('_')[0]}"))
    path = _FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")

class TestParseSeriesInfo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_series_info(_load_html("overview.html"))
        self.result.series_id = 542272

    def test_basic_info(self):
        assert self.result.series_id == 542272
        assert self.result.status == "completed"
        assert self.result.event_name == "Valorant Champions 2025"
        assert self.result.stage == "Playoffs"
        assert self.result.bracket == "Grand Final"

    def test_teams(self):
        assert self.result.team1.name == "NRG"
        assert self.result.team1.tag == "NRG"
        assert self.result.team1.id == 1034
        assert self.result.team2.name == "FNATIC"
        assert self.result.team2.tag == "FNC"
        assert self.result.team2.id == 2593

    def test_scores(self):
        assert self.result.score1 == 3
        assert self.result.score2 == 2
        assert self.result.best_of == 5

    def test_games(self):
        assert len(self.result.games) == 5

        game1 = self.result.games[0]
        assert game1.game_id == 233478
        assert game1.map_name == "Corrode"
        assert game1.picked_by == "NRG"
        assert game1.played is True
        assert game1.team1_score == 13
        assert game1.team2_score == 3
        assert game1.team1_defense_rounds == 9
        assert game1.team1_attack_rounds == 4
        assert game1.team2_attack_rounds == 3
        assert game1.team2_defense_rounds == 0
        assert game1.duration_seconds == 2434

        game2 = self.result.games[1]
        assert game2.game_id == 233479
        assert game2.map_name == "Lotus"
        assert game2.team1_score == 13
        assert game2.team2_score == 6
        assert game2.team1_defense_rounds == 4
        assert game2.team1_attack_rounds == 9
        assert game2.team2_attack_rounds == 3
        assert game2.team2_defense_rounds == 3
        assert game2.duration_seconds == 2688

        game3 = self.result.games[2]
        assert game3.game_id == 233480
        assert game3.map_name == "Abyss"
        assert game3.team1_score == 13
        assert game3.team2_score == 15
        assert game3.team1_defense_rounds == 11
        assert game3.team1_attack_rounds == 1
        assert game3.team1_overtime_rounds == 1
        assert game3.team2_attack_rounds == 1
        assert game3.team2_defense_rounds == 11
        assert game3.team2_overtime_rounds == 3
        assert game3.duration_seconds == 3813

        game4 = self.result.games[3]
        assert game4.game_id == 233481
        assert game4.map_name == "Ascent"
        assert game4.team1_score == 8
        assert game4.team2_score == 13
        assert game4.duration_seconds == 3167

        game5 = self.result.games[4]
        assert game5.game_id == 233482
        assert game5.map_name == "Sunset"
        assert game5.team1_score == 13
        assert game5.team2_score == 5
        assert game5.team1_defense_rounds == 4
        assert game5.team1_attack_rounds == 9
        assert game5.team2_attack_rounds == 2
        assert game5.team2_defense_rounds == 3
        assert game5.duration_seconds == 2538


_BO1_FIXTURES = FIXTURES_DIR / "series" / "704037"


def _load_bo1_html(filename: str) -> HTMLParser:
    path = _BO1_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseSeriesInfoBo1:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_series_info(_load_bo1_html("overview.html"))
        self.result.series_id = 704037

    def test_basic_info(self):
        assert self.result.series_id == 704037
        assert self.result.status == "completed"
        assert self.result.event_name == "Game Changers 2026: EMEA Stage 2 - Promotion/Relegation"
        assert self.result.stage == "Swiss Stage"
        assert self.result.bracket == "Round 1"

    def test_teams(self):
        assert self.result.team1.name == "Mushoku"
        assert self.result.team2.name == "Fallen Angels"

    def test_scores(self):
        assert self.result.score1 == 0
        assert self.result.score2 == 1
        assert self.result.best_of == 1

    def test_single_game(self):
        assert len(self.result.games) == 1

    def test_game_details(self):
        game = self.result.games[0]
        assert game.game_id == 274641
        assert game.map_name == "Pearl"
        assert game.order == 1
        assert game.played is True
        assert game.team1_score == 2
        assert game.team2_score == 13
        assert game.team1_defense_rounds == 2
        assert game.team1_attack_rounds == 0
        assert game.team2_attack_rounds == 10
        assert game.team2_defense_rounds == 3
        assert game.duration_seconds == 2148


_BO1_VETO_FIXTURES = FIXTURES_DIR / "series" / "64819"


def _load_bo1_veto_html(filename: str) -> HTMLParser:
    path = _BO1_VETO_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseSeriesInfoBo1WithDeciderVeto:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_series_info(_load_bo1_veto_html("overview.html"))
        self.result.series_id = 64819

    def test_basic_info(self):
        assert self.result.series_id == 64819
        assert self.result.status == "completed"
        assert self.result.best_of == 1

    def test_teams(self):
        assert self.result.team1.name == "Madness Esports"
        assert self.result.team2.name == "Huat Zai"

    def test_scores(self):
        assert self.result.score1 == 0
        assert self.result.score2 == 1

    def test_veto_parsed(self):
        assert len(self.result.veto) == 7
        assert self.result.veto[0].veto_type == "ban"
        assert self.result.veto[0].map_name == "Bind"
        assert self.result.veto[0].team == "MAD"
        assert self.result.veto[6].veto_type == "decider"
        assert self.result.veto[6].map_name == "Breeze"
        assert self.result.veto[6].team == ""

    def test_single_game(self):
        assert len(self.result.games) == 1

    def test_game_details(self):
        game = self.result.games[0]
        assert game.game_id == 65212
        assert game.map_name == "Breeze"
        assert game.order == 1
        assert game.played is True
        assert game.team1_score == 7
        assert game.team2_score == 13


_BO1_PICK_FIXTURES = FIXTURES_DIR / "series" / "30788"


def _load_bo1_pick_html(filename: str) -> HTMLParser:
    path = _BO1_PICK_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseSeriesInfoBo1WithPickVeto:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_series_info(_load_bo1_pick_html("overview.html"))
        self.result.series_id = 30788

    def test_basic_info(self):
        assert self.result.series_id == 30788
        assert self.result.status == "completed"
        assert self.result.best_of == 1

    def test_teams(self):
        assert self.result.team1.name == "Cynical"
        assert self.result.team2.name == "NXLG Academy"

    def test_scores(self):
        assert self.result.score1 == 1
        assert self.result.score2 == 0

    def test_veto_parsed(self):
        assert len(self.result.veto) == 1
        assert self.result.veto[0].veto_type == "pick"
        assert self.result.veto[0].map_name == "Icebox"
        assert self.result.veto[0].team == "NXLGA"

    def test_single_game(self):
        assert len(self.result.games) == 1

    def test_game_details(self):
        game = self.result.games[0]
        assert game.game_id == 47971
        assert game.map_name == "Icebox"
        assert game.order == 1
        assert game.played is True
        assert game.team1_score == 13
        assert game.team2_score == 11

