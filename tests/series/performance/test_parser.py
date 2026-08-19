import pytest

from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._series._utils import PlayerMap
from vlrdevapi._series.performance.parser import parse_performance_data
from vlrdevapi._series.players.parser import parse_players_stats
from vlrdevapi.exceptions import ParsingError


_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "542272_nrg-vs-fnatic-valorant-champions-2025-gf"
)


def _load_html(filename: str) -> HTMLParser:
    if _LIVE:
        series_id = _FIXTURES.name.split("_")[0]
        game_id = ""
        if "game_" in filename:
            game_id = filename.split("_")[1]
        url = f"/{series_id}/?tab=performance"
        if game_id:
            url += f"&game={game_id}"
        return HTMLParser(live_fetch(url))
    path = _FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


def _overview_mapping() -> PlayerMap:
    """Build a player map from the series overview fixture."""
    overview = _load_html("overview.html")
    stats = parse_players_stats(overview, game_id="all")
    mapping = PlayerMap()
    for team in [stats.team1, stats.team2]:
        for player in team.players:
            mapping.add(player.team_short, player.name, player.player_id)
    return mapping


class TestParsePerformanceGame233478:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"),
            game_id="233478",
            player_mapping=PlayerMap(),
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
        assert brawk.economy == 99
        assert brawk.defuses == 2

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
        assert crashies.plants == 4

    def test_adv_stats_alfajer(self):
        alfajer = self.result.adv_stats[9]
        assert alfajer.name == "Alfajer"
        assert alfajer.agent == "Vyse"
        assert alfajer.economy == 37


class TestParsePerformanceGameAll:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"), game_id="all", player_mapping=PlayerMap()
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
        assert brawk.economy == 66

    def test_adv_stats_alfajer(self):
        alfajer = self.result.adv_stats[9]
        assert alfajer.name == "Alfajer"
        assert alfajer.two_k == 14
        assert alfajer.economy == 51


class TestParsePerformanceInvalidGame:
    def test_raises_for_invalid_game(self):
        with pytest.raises(ParsingError, match="index out of range"):
            parse_performance_data(
                _load_html("game_233478_performance.html"),
                game_id="999999",
                player_mapping=PlayerMap(),
            )


class TestParsePerformancePositional:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_html("game_233478_performance.html")
        self.game1 = parse_performance_data(self.html, game_id=1, player_mapping=PlayerMap())
        self.game2 = parse_performance_data(self.html, game_id=2, player_mapping=PlayerMap())

    def test_positional_game_one_matches_real_id(self):
        real = parse_performance_data(self.html, game_id="233478", player_mapping=PlayerMap())
        assert self.game1.all_kills_matrix.entries == real.all_kills_matrix.entries
        assert [e.name for e in self.game1.adv_stats] == [e.name for e in real.adv_stats]

    def test_positional_game_one_non_empty(self):
        assert len(self.game1.all_kills_matrix.entries) == 25
        assert len(self.game1.adv_stats) == 10

    def test_positional_game_one_top_player(self):
        brawk = self.game1.adv_stats[0]
        assert brawk.name == "brawk"
        assert brawk.agent == "Sova"
        assert brawk.two_k == 5
        assert brawk.economy == 99

    def test_positional_game_two_differs_from_game_one(self):
        brawk1 = self.game1.adv_stats[0]
        brawk2 = self.game2.adv_stats[0]
        assert brawk1.agent == "Sova"
        assert brawk2.agent == "Vyse"
        assert brawk1.two_k == 5
        assert brawk2.two_k == 1
        assert brawk1.economy == 99
        assert brawk2.economy == 51


class TestParsePerformancePlayerIds:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_performance_data(
            _load_html("game_233478_performance.html"),
            game_id="233478",
            player_mapping=_overview_mapping(),
        )

    def test_adv_stats_player_ids_resolved_from_overview(self):
        by_name = {e.name: e for e in self.result.adv_stats}
        expected = {
            "brawk": 2172,
            "Ethan": 11225,
            "skuba": 11118,
            "mada": 5132,
            "s0m": 4164,
            "kaajak": 9554,
            "Alfajer": 9810,
            "Chronicle": 458,
            "crashies": 4,
            "Boaster": 438,
        }
        for name, player_id in expected.items():
            assert by_name[name].player_id == player_id

    def test_adv_stats_team_short_preserved(self):
        brawk = self.result.adv_stats[0]
        assert brawk.player_id == 2172
        assert brawk.team_short == "NRG"

    def test_kill_matrix_ids_resolved(self):
        for entry in self.result.all_kills_matrix.entries:
            assert entry.killer_id != 0
            assert entry.victim_id != 0
        e = self.result.all_kills_matrix.lookup("brawk", "Chronicle")
        assert e.killer_id == 2172
        assert e.victim_id == 458

    def test_notable_round_victim_ids_resolved(self):
        brawk = self.result.adv_stats[0]
        victim_ids = {
            v.name: v.player_id for r in brawk.two_k_rounds for v in r.victims
        }
        assert victim_ids["Chronicle"] == 458
        assert victim_ids["crashies"] == 4
        assert victim_ids["Boaster"] == 438
        assert all(pid is not None for pid in victim_ids.values())

    def test_renamed_fields(self):
        brawk = self.result.adv_stats[0]
        crashies = self.result.adv_stats[5]
        assert brawk.economy == 99
        assert brawk.defuses == 2
        assert crashies.plants == 4
        assert not hasattr(brawk, "econ")
        assert not hasattr(brawk, "pl")
        assert not hasattr(brawk, "de")

