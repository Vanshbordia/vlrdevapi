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
        series_id = _FIXTURES.name.split("_")[0]
        return HTMLParser(live_fetch(f"/{series_id}"))
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

