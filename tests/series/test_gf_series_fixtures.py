"""Integration tests for the two grand-final fixture series across tabs.

Values below were verified against the live vlr.gg pages for:
- Series 130685: LOUD vs OpTic Gaming, Valorant Champions 2022 Grand Final
- Series 754737: LOUD vs Team Vitality, Valorant Champions 2026 Grand Final
"""

import pytest
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import _LIVE, FIXTURES_DIR, live_fetch
from vlrdevapi._series.economy.models import BuyTierRecord, EconScore
from vlrdevapi._series.economy.parser import parse_economy_data
from vlrdevapi._series.info.parser import parse_series_info
from vlrdevapi._series.performance.parser import parse_performance_data
from vlrdevapi._series.players.parser import parse_players_stats
from vlrdevapi._series.rounds.parser import parse_rounds_data

SERIES = {
    130685: "130685_loud-vs-optic-gaming-valorant-champions-2022-gf",
    754737: "754737_loud-vs-team-vitality-valorant-champions-2026-gf",
}


def _load(series_id: int, filename: str) -> HTMLParser:
    if _LIVE:
        stem = filename.split("_")
        tab = stem[-1].replace(".html", "") if "economy" in filename else "overview"
        game_id = stem[1] if len(stem) > 3 else None
        url = f"/{series_id}/?game={game_id}&tab={tab}" if game_id else f"/{series_id}/"
        return HTMLParser(live_fetch(url))
    path = FIXTURES_DIR / "series" / SERIES[series_id] / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestChampions2022GFInfo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load(130685, "overview.html")
        self.info = parse_series_info(self.html)

    def test_teams_and_score(self):
        assert self.info.team1.name == "LOUD"
        assert self.info.team1.id == 6961
        assert self.info.team2.name == "OpTic Gaming"
        assert self.info.team2.id == 8127
        assert self.info.score1 == 3
        assert self.info.score2 == 1
        assert self.info.best_of == 5
        assert self.info.event_name == "Valorant Champions 2022"
        assert self.info.stage == "Playoffs"
        assert self.info.bracket == "Grand Final"

    def test_pick_bans(self):
        veto = [(v.veto_type, v.team, v.map_name) for v in self.info.veto]
        assert veto == [
            ("ban", "LOUD", "Pearl"),
            ("ban", "LOUD", "Fracture"),
            ("pick", "LOUD", "Ascent"),
            ("pick", "OPTC", "Bind"),
            ("pick", "LOUD", "Breeze"),
            ("pick", "OPTC", "Haven"),
            ("decider", "", "Icebox"),
        ]

    def test_games(self):
        games = [
            (g.map_name, g.picked_by, g.played, g.team1_score, g.team2_score)
            for g in self.info.games
        ]
        assert games == [
            ("Ascent", "LOUD", True, 15, 13),
            ("Bind", "OPTC", True, 6, 13),
            ("Breeze", "LOUD", True, 16, 14),
            ("Haven", "OPTC", True, 13, 5),
            ("Icebox", "", False, None, None),
        ]


class TestChampions2022GFPlayers:
    def test_all_maps_player_stats(self):
        html = _load(130685, "overview.html")
        players = parse_players_stats(html, game_id="all")
        assert players.team1.team_name == "LOUD"
        assert players.team1.team_id == 6961
        assert players.team2.team_name == "OpTic Gaming"
        assert players.team2.team_id == 8127
        assert len(players.team1.players) == 5
        assert len(players.team2.players) == 5
        sacy = next(p for p in players.team1.players if p.name == "Sacy")
        assert sacy.player_id == 659
        assert sorted(sacy.agents) == ["Fade", "Sova"]
        assert sacy.stats.overall.rating == 1.31
        assert sacy.stats.overall.acs == 208.0
        assert sacy.stats.overall.kd_diff == 19


class TestChampions2022GFRounds:
    def test_ascent_overtime_round_count(self):
        html = _load(130685, "game_95131_overview.html")
        rounds = parse_rounds_data(html, game_id=95131)
        assert len(rounds.rounds) == 28
        assert rounds.rounds[0].side == "Attack"
        assert {r.win_type for r in rounds.rounds} == {
            "Defuse",
            "Elimination",
            "Spike detonation",
        }

    def test_other_maps_parse(self):
        expected = {95132: 19, 95133: 30, 95134: 18}
        for game_id, n in expected.items():
            html = _load(130685, f"game_{game_id}_overview.html")
            rounds = parse_rounds_data(html, game_id=game_id)
            assert len(rounds.rounds) == n


class TestChampions2022GFPerformance:
    def test_kill_matrix_and_adv_stats(self):
        html = _load(130685, "game_95131_performance.html")
        perf = parse_performance_data(html, game_id=95131)
        assert len(perf.all_kills_matrix.entries) == 25
        assert len(perf.first_kills_matrix.entries) == 25
        assert len(perf.adv_stats) == 10
        sacy = next(e for e in perf.adv_stats if e.name == "Sacy")
        assert sacy.team_short == "LOUD"
        assert sacy.agent == "Sova"
        assert sacy.two_k == 4
        assert sacy.three_k == 4
        assert sacy.four_k == 1
        assert sacy.one_v1 == 2


class TestChampions2026GFInfo:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load(754737, "overview.html")
        self.info = parse_series_info(self.html)

    def test_teams_and_score(self):
        assert self.info.team1.name == "LOUD"
        assert self.info.team1.id == 6961
        assert self.info.team2.name == "Team Vitality"
        assert self.info.team2.id == 2059
        assert self.info.score1 == 3
        assert self.info.score2 == 1
        assert self.info.best_of == 5
        assert self.info.event_name == "Valorant Champions 2026"
        assert self.info.stage == "Playoffs"
        assert self.info.bracket == "Grand Final"
        assert self.info.patch == "13.05"

    def test_pick_bans(self):
        veto = [(v.veto_type, v.team, v.map_name) for v in self.info.veto]
        assert veto == [
            ("ban", "LOUD", "Ascent"),
            ("ban", "LOUD", "Split"),
            ("pick", "LOUD", "Summit"),
            ("pick", "VIT", "Lotus"),
            ("pick", "LOUD", "Sunset"),
            ("pick", "VIT", "Haven"),
            ("decider", "", "Abyss"),
        ]

    def test_games(self):
        games = [
            (g.map_name, g.picked_by, g.played, g.team1_score, g.team2_score, g.game_id)
            for g in self.info.games
        ]
        assert games == [
            ("Summit", "LOUD", True, 13, 11, 283286),
            ("Lotus", "VIT", True, 8, 13, 283287),
            ("Sunset", "LOUD", True, 13, 5, 283288),
            ("Haven", "VIT", True, 13, 10, 283289),
            ("Abyss", "", False, None, None, 283290),
        ]


class TestChampions2026GFPlayers:
    def test_all_maps_player_stats(self):
        html = _load(754737, "overview.html")
        players = parse_players_stats(html, game_id="all")
        assert players.team1.team_name == "LOUD"
        assert players.team1.team_id == 6961
        assert players.team2.team_name == "Team Vitality"
        assert players.team2.team_id == 2059
        assert len(players.team1.players) == 5
        assert len(players.team2.players) == 5
        erde = next(p for p in players.team1.players if p.name == "erde")
        assert erde.player_id == 29242
        assert sorted(erde.agents) == ["Omen", "Sage"]
        assert erde.stats.overall.rating == 1.13
        assert erde.stats.overall.acs == 222.0
        assert erde.stats.overall.kd_diff == 10
        chronicle = next(p for p in players.team2.players if p.name == "Chronicle")
        assert chronicle.player_id == 458
        assert chronicle.stats.overall.acs == 201.0


class TestChampions2026GFRounds:
    def test_summit_round_count(self):
        html = _load(754737, "game_283286_overview.html")
        rounds = parse_rounds_data(html, game_id=283286)
        assert len(rounds.rounds) == 24
        assert rounds.rounds[0].side == "Defense"
        assert {r.win_type for r in rounds.rounds} == {
            "Defuse",
            "Elimination",
            "Time out",
        }

    def test_other_maps_parse(self):
        expected = {283287: 21, 283288: 18, 283289: 23}
        for game_id, n in expected.items():
            html = _load(754737, f"game_{game_id}_overview.html")
            rounds = parse_rounds_data(html, game_id=game_id)
            assert len(rounds.rounds) == n


class TestChampions2026GFPerformance:
    def test_kill_matrix_and_adv_stats(self):
        html = _load(754737, "game_283286_performance.html")
        perf = parse_performance_data(html, game_id=283286)
        assert len(perf.all_kills_matrix.entries) == 25
        assert len(perf.first_kills_matrix.entries) == 25
        assert len(perf.adv_stats) == 10
        darker = next(e for e in perf.adv_stats if e.name == "Darker")
        assert darker.team_short == "LOUD"
        assert darker.agent == "Omen"
        assert darker.two_k == 5
        assert darker.three_k == 1
        assert darker.economy == 58
        assert darker.plants == 2
        assert darker.defuses == 1


class TestChampions2022GFEconomyAllGames:
    """Per-map matrix values (game 1 covers every map's economy section)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load(130685, "game_95131_economy.html")

    def _game(self, game_id):
        return parse_economy_data(self.html, game_id=game_id)

    def test_bind(self):
        game = self._game(95132)
        m1, m2 = game.buy_matrix_team1, game.buy_matrix_team2
        assert len(game.rounds) == 19
        assert m1.pistol == EconScore(won=1, total=2)
        assert m1.on_full_buy == BuyTierRecord(
            vs_eco=None,
            vs_half=EconScore(won=1, total=2),
            vs_full=EconScore(won=2, total=8),
        )
        assert m2.on_full_buy == BuyTierRecord(
            vs_eco=None,
            vs_half=EconScore(won=3, total=3),
            vs_full=EconScore(won=6, total=8),
        )

    def test_breeze(self):
        game = self._game(95133)
        m1 = game.buy_matrix_team1
        assert len(game.rounds) == 24
        assert game.pistol_team1 == EconScore(won=1, total=2)
        assert m1.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=2, total=3),
        )
        assert m1.on_full_buy.total == EconScore(won=7, total=14)

    def test_haven(self):
        game = self._game(95134)
        m1, m2 = game.buy_matrix_team1, game.buy_matrix_team2
        assert len(game.rounds) == 18
        assert game.pistol_team1 == EconScore(won=2, total=2)
        assert m1.converted == EconScore(won=2, total=2)
        assert m1.bonus == EconScore(won=2, total=2)
        assert m2.pistol == EconScore(won=0, total=2)
        assert m2.converted is None
        assert m2.bonus is None
