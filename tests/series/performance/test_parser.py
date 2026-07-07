import pytest

from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._series.performance.parser import parse_performance_data


_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "542272_nrg-vs-fnatic-valorant-champions-2025-gf"
)


def _load_html(filename: str) -> HTMLParser:
    path = _FIXTURES / filename
    return HTMLParser(path.read_text(encoding="utf-8"))


class TestParsePerformanceGame233478:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"),
            game_id="233478",
            player_mapping={},
        )

    def test_all_kills_matrix_entries_count(self):
        assert len(self.result.all_kills_matrix.entries) == 25

    def test_notable_rounds_have_victims_with_ids(self):
        brawk = self.result.adv_stats[0]
        assert brawk.two_k_rounds
        for round in brawk.two_k_rounds:
            for victim in round.victims:
                assert hasattr(victim, "name")
                assert hasattr(victim, "player_id")

    def test_all_kills_matrix_killers(self):
        assert self.result.all_kills_matrix.killers() == [
            "brawk",
            "Ethan",
            "s0m",
            "mada",
            "skuba",
        ]

    def test_all_kills_matrix_victims(self):
        assert self.result.all_kills_matrix.victims() == [
            "Chronicle",
            "crashies",
            "Boaster",
            "kaajak",
            "Alfajer",
        ]

    def test_all_kills_lookup_brawk_chronicle(self):
        e = self.result.all_kills_matrix.lookup("brawk", "Chronicle")
        assert e is not None
        assert e.killer == "brawk"
        assert e.killer_team == "NRG"
        assert e.victim == "Chronicle"
        assert e.victim_team == "FNC"
        assert e.kills == 8
        assert e.deaths == 0
        assert e.diff == 8

    def test_all_kills_lookup_ethan_kaajak(self):
        e = self.result.all_kills_matrix.lookup("Ethan", "kaajak")
        assert e is not None
        assert e.kills == 2
        assert e.deaths == 4
        assert e.diff == -2

    def test_all_kills_by_killer_brawk(self):
        entries = self.result.all_kills_matrix.by_killer("brawk")
        assert len(entries) == 5
        assert all(e.killer == "brawk" for e in entries)
        assert all(e.killer_team == "NRG" for e in entries)
        victims = [e.victim for e in entries]
        assert "Chronicle" in victims
        assert "Alfajer" in victims

    def test_all_kills_by_victim_chronicle(self):
        entries = self.result.all_kills_matrix.by_victim("Chronicle")
        assert len(entries) == 5
        assert all(e.victim == "Chronicle" for e in entries)
        assert all(e.victim_team == "FNC" for e in entries)

    def test_all_kills_by_team(self):
        entries = self.result.all_kills_matrix.by_team("NRG")
        assert len(entries) == 25
        fnc_entries = self.result.all_kills_matrix.by_team("FNC")
        assert len(fnc_entries) == 25

    def test_all_kills_lookup_nonexistent(self):
        e = self.result.all_kills_matrix.lookup("nonexistent", "Chronicle")
        assert e is None

    def test_first_kills_matrix_entries(self):
        fk = self.result.first_kills_matrix
        assert len(fk.entries) == 25

        e = fk.lookup("brawk", "crashies")
        assert e is not None
        assert e.kills == 1
        assert e.deaths == 0
        assert e.diff == 1

    def test_first_kills_matrix_null_as_zero(self):
        fk = self.result.first_kills_matrix
        e = fk.lookup("s0m", "Chronicle")
        assert e is not None
        assert e.kills is None
        assert e.deaths is None
        assert e.diff is None

    def test_op_kills_matrix_entries(self):
        op = self.result.op_kills_matrix
        assert len(op.entries) == 25

        e = op.lookup("mada", "Chronicle")
        assert e is not None
        assert e.kills == 2
        assert e.deaths == 0
        assert e.diff == 2

    def test_adv_stats_count(self):
        assert len(self.result.adv_stats) == 10

    def test_adv_stats_brawk(self):
        brawk = self.result.adv_stats[0]
        assert brawk.name == "brawk"
        assert brawk.team_short == "NRG"
        assert brawk.agent == "Sova"
        assert brawk.two_k == 5
        assert brawk.three_k == 3
        assert brawk.econ == 99
        assert brawk.de == 2

    def test_adv_stats_skuba(self):
        skuba = self.result.adv_stats[3]
        assert skuba.name == "skuba"
        assert skuba.agent == "Viper"
        assert skuba.three_k == 1
        assert skuba.one_v2 == 1

    def test_adv_stats_crashies(self):
        crashies = self.result.adv_stats[5]
        assert crashies.name == "crashies"
        assert crashies.team_short == "FNC"
        assert crashies.agent == "Fade"
        assert crashies.one_v1 == 1
        assert crashies.pl == 4

    def test_adv_stats_alfajer(self):
        alfajer = self.result.adv_stats[9]
        assert alfajer.name == "Alfajer"
        assert alfajer.agent == "Vyse"
        assert alfajer.econ == 37


class TestParsePerformanceGameAll:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"), game_id="all", player_mapping={}
        )

    def test_all_kills_matrix_entries(self):
        assert len(self.result.all_kills_matrix.entries) == 25

    def test_all_kills_lookup_brawk_chronicle(self):
        e = self.result.all_kills_matrix.lookup("brawk", "Chronicle")
        assert e is not None
        assert e.kills == 22
        assert e.deaths == 15
        assert e.diff == 7

    def test_all_kills_lookup_ethan_kaajak(self):
        e = self.result.all_kills_matrix.lookup("Ethan", "kaajak")
        assert e is not None
        assert e.kills == 12
        assert e.deaths == 23
        assert e.diff == -11

    def test_adv_stats_brawk(self):
        brawk = self.result.adv_stats[0]
        assert brawk.name == "brawk"
        assert brawk.two_k == 12
        assert brawk.three_k == 8
        assert brawk.econ == 66

    def test_adv_stats_alfajer(self):
        alfajer = self.result.adv_stats[9]
        assert alfajer.name == "Alfajer"
        assert alfajer.two_k == 14
        assert alfajer.econ == 51


class TestParsePerformanceInvalidGame:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"),
            game_id="999999",
            player_mapping={},
        )

    def test_empty_result_for_invalid_game(self):
        assert self.result.all_kills_matrix.entries == []
        assert self.result.adv_stats == []

