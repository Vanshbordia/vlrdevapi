import pytest
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import _LIVE, FIXTURES_DIR, live_fetch
from vlrdevapi._series.economy.models import BuyTierRecord, EconScore
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
        assert round_1.spent_team1 == 3700
        assert round_1.spent_team2 == 3600

    def test_game_two_differs_from_game_one(self):
        assert len(self.game1.rounds) == 16
        assert len(self.game2.rounds) == 19
        round_1 = self.game2.rounds[0]
        assert round_1.spent_team1 == 3800
        assert round_1.spent_team2 == 3400

    def test_positional_game_one_matches_real_id(self):
        real = parse_economy_data(self.html, game_id="233478")
        assert len(real.rounds) == len(self.game1.rounds) == 16
        assert [r.spent_team1 for r in real.rounds] == [
            r.spent_team1 for r in self.game1.rounds
        ]

    def test_unplayed_grid_columns_are_skipped(self):
        # The real ECR grid always renders a column per possible round, but
        # game 1 ended at round 16. The blank (unplayed) columns carry no
        # spend title and must be dropped, leaving contiguous round numbers.
        game = self.html.css_first('.vm-stats-game[data-game-id="233478"]')
        grid_cols = [
            col
            for col in game.css(".vlr-rounds.ecr .vlr-rounds-row-col")
            if "mod-teams" not in (col.attributes.get("class") or "")
        ]
        assert len(grid_cols) > len(self.game1.rounds)
        assert [r.round_number for r in self.game1.rounds] == list(
            range(1, len(self.game1.rounds) + 1)
        )

    def test_every_buy_level_is_decoded(self):
        buys = set()
        for round_data in self.game1.rounds:
            buys.add(round_data.buy_type_team1)
            buys.add(round_data.buy_type_team2)
        assert buys == {"Pistol", "Eco", "Half-buy", "Full-buy"}

    def test_buy_matrix_summary(self):
        # Values read off the vlr.gg economy tab for NRG (team 1).
        matrix = self.game1.buy_matrix_team1
        assert matrix.pistol == EconScore(won=1, total=2)
        assert matrix.converted == EconScore(won=1, total=1)
        assert matrix.bonus == EconScore(won=1, total=1)

    def test_buy_matrix_tiers(self):
        matrix = self.game1.buy_matrix_team1
        assert matrix.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=1, total=1),
            vs_half=EconScore(won=4, total=5),
            vs_full=EconScore(won=4, total=4),
        )
        assert matrix.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=None,
        )

    def test_round_winner_side_removed(self):
        # Winner side lives in series.rounds (RoundData.side); economy
        # rounds intentionally do not duplicate it.
        assert not hasattr(self.game1.rounds[0], "winner_side")


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


# ── Series 130685 (Champions 2022 GF, LOUD vs OpTic) ─────────
_2022_GF_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "130685_loud-vs-optic-gaming-valorant-champions-2022-gf"
)


def _load_2022_gf_html(filename: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch("/130685/?game=95131&tab=economy"))
    path = _2022_GF_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestChampions2022GFEconomy:
    """Values verified against the live Champions 2022 GF economy tab."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_2022_gf_html("game_95131_economy.html")

    def _game(self, game_id):
        return parse_economy_data(self.html, game_id=game_id)

    # Ascent (game 95131) — values read off the live page.
    def test_ascent_matrix_summary(self):
        game = self._game(95131)
        assert len(game.rounds) == 24
        assert game.team1 == "LOUD"
        assert game.team2 == "OPTC"
        assert game.pistol_team1 == EconScore(won=1, total=2)
        assert game.converted_team1 == EconScore(won=1, total=1)
        assert game.bonus_team1 == EconScore(won=0, total=1)
        assert game.pistol_team2 == EconScore(won=1, total=2)
        assert game.converted_team2 == EconScore(won=1, total=1)
        assert game.bonus_team2 == EconScore(won=0, total=1)

    def test_ascent_matrix_tiers(self):
        game = self._game(95131)
        m1, m2 = game.buy_matrix_team1, game.buy_matrix_team2
        assert m1.on_eco == BuyTierRecord(vs_eco=None, vs_half=None, vs_full=None)
        assert m1.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=1, total=4),
        )
        assert m1.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=1, total=1),
            vs_half=EconScore(won=1, total=2),
            vs_full=EconScore(won=6, total=11),
        )
        assert m2.on_eco == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=0, total=1),
        )
        assert m2.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=1, total=2),
        )
        assert m2.on_full_buy == BuyTierRecord(
            vs_eco=None, vs_half=EconScore(won=3, total=4),
            vs_full=EconScore(won=5, total=11),
        )

    def test_ascent_tier_combined_total(self):
        game = self._game(95131)
        m1 = game.buy_matrix_team1
        assert m1.on_full_buy.total == EconScore(won=8, total=14)
        assert m1.on_half_buy.total == EconScore(won=1, total=4)
        assert m1.on_eco.total is None

    def test_ascent_first_round(self):
        round_1 = self._game(95131).rounds[0]
        assert round_1.bank_team1 == 400.0
        assert round_1.bank_team2 == 100.0
        assert round_1.spent_team1 == 3800
        assert round_1.spent_team2 == 3700
        assert round_1.buy_type_team1 == "Pistol"
        assert round_1.buy_type_team2 == "Pistol"
        assert round_1.is_pistol_round is True

    def test_all_maps_summary(self):
        game = self._game("all")
        assert game.rounds == []
        assert game.team1 == "LOUD"
        assert game.team2 == "OPTC"
        assert game.pistol_team1 == EconScore(won=5, total=8)
        assert game.bonus_team2 == EconScore(won=2, total=3)
        m1 = game.buy_matrix_team1
        assert m1.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=2, total=2),
            vs_half=EconScore(won=4, total=8),
            vs_full=EconScore(won=18, total=38),
        )

    # Per-map matrix sanity across the rest of the series.
    def test_icebox_convert_never_happens(self):
        game = self._game(95134)
        m2 = game.buy_matrix_team2
        assert m2.pistol == EconScore(won=0, total=2)
        assert m2.converted is None
        assert m2.bonus is None

    def test_every_game_parses(self):
        for game_id in (95131, 95132, 95133, 95134):
            game = self._game(game_id)
            assert len(game.rounds) > 0
            assert game.pistol_team1 is not None


# ── Series 754737 (Champions 2026 GF, LOUD vs Vitality) ──────
_2026_GF_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "754737_loud-vs-team-vitality-valorant-champions-2026-gf"
)


def _load_2026_gf_html(filename: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch("/754737/?game=283286&tab=economy"))
    path = _2026_GF_FIXTURES / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestChampions2026GFEconomy:
    """Values verified against the live Champions 2026 GF economy tab."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.html = _load_2026_gf_html("game_283286_economy.html")

    def _game(self, game_id):
        return parse_economy_data(self.html, game_id=game_id)

    def test_summit_matrix_summary(self):
        game = self._game(283286)
        assert len(game.rounds) == 24
        assert game.team1 == "LOUD"
        assert game.team2 == "VIT"
        assert game.pistol_team1 == EconScore(won=1, total=2)
        assert game.converted_team1 == EconScore(won=1, total=1)
        assert game.bonus_team1 == EconScore(won=0, total=1)
        assert game.pistol_team2 == EconScore(won=1, total=2)
        assert game.converted_team2 == EconScore(won=1, total=1)
        assert game.bonus_team2 == EconScore(won=0, total=1)

    def test_summit_matrix_tiers(self):
        game = self._game(283286)
        m1, m2 = game.buy_matrix_team1, game.buy_matrix_team2
        assert m1.on_eco == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=0, total=1),
        )
        assert m1.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=0, total=1),
        )
        assert m1.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=1, total=2),
            vs_half=EconScore(won=2, total=2),
            vs_full=EconScore(won=7, total=12),
        )
        assert m2.on_eco == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=1, total=2),
        )
        assert m2.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=0, total=2),
        )
        assert m2.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=1, total=1),
            vs_half=EconScore(won=1, total=1),
            vs_full=EconScore(won=5, total=12),
        )

    def test_summit_combined_totals(self):
        game = self._game(283286)
        m1 = game.buy_matrix_team1
        assert m1.full_buy.total == EconScore(won=10, total=16)
        assert m1.half_buy.total == EconScore(won=0, total=1)
        # Alias properties point at the canonical fields.
        assert m1.full_buy is m1.on_full_buy
        assert m1.half_buy is m1.on_half_buy
        assert m1.eco is m1.on_eco

    def test_lotus_never_converted(self):
        # Lotus (283287): LOUD lost both pistols, so conv./bonus never ran.
        game = self._game(283287)
        assert len(game.rounds) == 21
        m1, m2 = game.buy_matrix_team1, game.buy_matrix_team2
        assert m1.pistol == EconScore(won=0, total=2)
        assert m1.converted is None
        assert m1.bonus is None
        assert m2.pistol == EconScore(won=2, total=2)
        assert m2.converted == EconScore(won=2, total=2)
        assert m2.bonus == EconScore(won=1, total=2)

    def test_sunset_first_round(self):
        round_1 = self._game(283288).rounds[0]
        assert round_1.bank_team1 == 0.0
        assert round_1.bank_team2 == 100.0
        assert round_1.spent_team1 == 4000
        assert round_1.spent_team2 == 3900
        assert round_1.buy_type_team1 == "Pistol"
        assert round_1.buy_type_team2 == "Pistol"

    def test_every_game_parses(self):
        for game_id in (283286, 283287, 283288, 283289):
            game = self._game(game_id)
            assert len(game.rounds) > 0
            assert game.pistol_team1 is not None
            assert game.pistol_team2 is not None
